import json
import logging
import secrets
import urllib.parse

import jwt as pyjwt
import requests
from constance import config
from django.contrib.auth import login as auth_login
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

SSO_STATE_TIMEOUT = 600


def _get_allowed_hosts():
    from django.conf import settings

    hosts = set(settings.ALLOWED_HOSTS)
    frontend_url = config.OIDC_REDIRECT_URL
    if frontend_url:
        parsed = urllib.parse.urlparse(frontend_url)
        if parsed.hostname:
            hosts.add(parsed.hostname)
    return list(hosts)


def _is_safe_redirect(url):
    allowed = _get_allowed_hosts()
    return url_has_allowed_host_and_scheme(url, allowed_hosts=allowed if allowed else None)


class SsoLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not config.OIDC_ENABLED:
            return Response(
                {"error": "SSO is not enabled"},
                status=status.HTTP_404_NOT_FOUND,
            )

        state = secrets.token_urlsafe(32)
        next_url = request.GET.get("next", config.OIDC_REDIRECT_URL)

        if not _is_safe_redirect(next_url):
            next_url = config.OIDC_REDIRECT_URL

        cache.set(f"sso_state_{state}", next_url, timeout=SSO_STATE_TIMEOUT)

        redirect_uri = request.build_absolute_uri(reverse("sso-callback"))
        params = {
            "response_type": "code",
            "client_id": config.OIDC_RP_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": config.OIDC_RP_SCOPES,
            "state": state,
        }
        auth_url = f"{config.OIDC_OP_AUTHORIZATION_ENDPOINT}?{urllib.parse.urlencode(params)}"
        return HttpResponseRedirect(auth_url)


class SsoCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def _exchange_code(self, code, redirect_uri):
        token_response = requests.post(
            config.OIDC_OP_TOKEN_ENDPOINT,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": config.OIDC_RP_CLIENT_ID,
                "client_secret": config.OIDC_RP_CLIENT_SECRET,
            },
            timeout=30,
        )
        token_response.raise_for_status()
        return token_response.json()

    def _get_jwks(self):
        jwks_response = requests.get(
            config.OIDC_OP_JWKS_ENDPOINT,
            timeout=30,
        )
        jwks_response.raise_for_status()
        return jwks_response.json()

    def _get_userinfo(self, access_token):
        if not config.OIDC_OP_USER_ENDPOINT:
            logger.warning("SSO: OIDC_OP_USER_ENDPOINT not configured, skipping UserInfo")
            return {}
        try:
            userinfo_response = requests.get(
                config.OIDC_OP_USER_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30,
            )
            userinfo_response.raise_for_status()
            data = userinfo_response.json()
            logger.debug("SSO: UserInfo fetched, keys=%s", list(data.keys()))
            return data
        except Exception as e:
            logger.warning("SSO: UserInfo fetch failed: %s", e)
            return {}

    def _verify_id_token(self, id_token, jwks_data):
        unverified_header = pyjwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg", "")

        signing_key = None

        if alg and alg.startswith("HS"):
            signing_key = config.OIDC_RP_CLIENT_SECRET
        elif jwks_data:
            for key_data in jwks_data.get("keys", []):
                kty = key_data.get("kty", "")
                if kid and key_data.get("kid") != kid:
                    continue
                if kty in ("RSA",):
                    signing_key = pyjwt.algorithms.RSAAlgorithm.from_jwk(
                        json.dumps(key_data)
                    )
                elif kty in ("EC",):
                    signing_key = pyjwt.algorithms.ECAlgorithm.from_jwk(
                        json.dumps(key_data)
                    )
                elif kty in ("OKP",):
                    signing_key = pyjwt.algorithms.OKPAlgorithm.from_jwk(
                        json.dumps(key_data)
                    )
                if signing_key is not None:
                    break

        if signing_key is None:
            raise pyjwt.InvalidKeyError("Invalid token signing key")

        return pyjwt.decode(
            id_token,
            signing_key,
            algorithms=[config.OIDC_RP_SIGN_ALGO],
            audience=config.OIDC_RP_CLIENT_ID,
            options={"verify_exp": True},
        )

    def get(self, request):
        if not config.OIDC_ENABLED:
            return Response(
                {"error": "SSO is not enabled"},
                status=status.HTTP_404_NOT_FOUND,
            )

        code = request.GET.get("code")
        state = request.GET.get("state", "")

        if not code:
            return JsonResponse(
                {"error": "Authorization code not provided"},
                status=400,
            )

        if not state:
            return JsonResponse(
                {"error": "Missing state parameter"},
                status=400,
            )

        next_url = cache.get(f"sso_state_{state}")
        if next_url is None:
            logger.warning("SSO callback with invalid or expired state")
            return JsonResponse(
                {"error": "Invalid or expired state parameter"},
                status=400,
            )
        cache.delete(f"sso_state_{state}")

        try:
            redirect_uri = request.build_absolute_uri(reverse("sso-callback"))

            token_data = self._exchange_code(code, redirect_uri)
            id_token = token_data.get("id_token", "")

            if not id_token:
                return JsonResponse(
                    {"error": "Authentication failed"},
                    status=400,
                )

            jwks_data = self._get_jwks()
            claims = self._verify_id_token(id_token, jwks_data)
            logger.debug("SSO: ID token claims keys=%s", list(claims.keys()))

            userinfo = self._get_userinfo(token_data.get("access_token", ""))
            if userinfo:
                claims = {**claims, **userinfo}
                logger.debug("SSO: merged claims keys=%s", list(claims.keys()))
            else:
                logger.debug("SSO: no userinfo data returned")

            from ngen.backends import NgenOidcBackend

            backend = NgenOidcBackend()
            user = backend.authenticate(
                request,
                claims=claims,
                id_token=id_token,
                access_token=token_data.get("access_token", ""),
            )

            if not user:
                return JsonResponse(
                    {"error": "User not found or not authorized"},
                    status=401,
                )

            auth_login(request, user, backend="ngen.backends.NgenOidcBackend")

            refresh = RefreshToken.for_user(user)
            access_jwt = str(refresh.access_token)

            from django.contrib.auth.models import Permission
            from rest_framework.reverse import reverse as drf_reverse

            perms = (
                Permission.objects.filter(group__in=user.groups.all())
                | user.user_permissions.all()
            )
            perms = sorted({p.codename for p in perms.distinct()})

            if user.priority:
                priority_url = drf_reverse(
                    "priority-detail",
                    kwargs={"pk": user.priority.id},
                    request=request,
                )
            else:
                priority_url = None

            user_data = {
                "id": user.id,
                "url": drf_reverse(
                    "user-detail",
                    kwargs={"pk": user.id},
                    request=request,
                ),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "priority": priority_url,
                "last_login": str(user.last_login) if user.last_login else None,
                "date_joined": str(user.date_joined) if user.date_joined else None,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "is_network_admin": user.is_network_admin,
                "permissions": perms,
            }

            exchange_code = secrets.token_urlsafe(32)
            cache.set(
                f"sso_exchange_{exchange_code}",
                {"access_token": access_jwt, "user_data": user_data},
                timeout=120,
            )

            frontend_url = config.OIDC_REDIRECT_URL or ""
            if not frontend_url:
                logger.error("SSO: OIDC_REDIRECT_URL is not configured")
                return JsonResponse(
                    {"error": "SSO misconfigured"},
                    status=500,
                )
            frontend_url = frontend_url.rstrip("/")

            redirect_url = (
                f"{frontend_url}/sso-callback"
                f"?code={exchange_code}"
                f"&next={urllib.parse.quote(next_url)}"
            )

            response = HttpResponseRedirect(redirect_url)
            response.set_cookie(
                "refresh_token",
                str(refresh),
                max_age=3600 * 24 * 14,
                httponly=True,
                path=reverse("ctoken-refresh"),
            )
            return response

        except pyjwt.ExpiredSignatureError:
            logger.warning("SSO token expired")
            return JsonResponse({"error": "Token expired"}, status=401)
        except pyjwt.InvalidAudienceError:
            logger.warning("SSO token audience mismatch")
            return JsonResponse({"error": "Token audience mismatch"}, status=401)
        except pyjwt.InvalidSignatureError:
            logger.warning("SSO token signature invalid")
            return JsonResponse({"error": "Token signature invalid"}, status=401)
        except (pyjwt.PyJWTError, ValueError) as e:
            logger.warning("SSO token verification failed: %s", e)
            return JsonResponse(
                {"error": "Token verification failed"},
                status=401,
            )
        except requests.RequestException:
            logger.exception("SSO provider connection failed")
            return JsonResponse(
                {"error": "Authentication service unavailable"},
                status=502,
            )
        except Exception:
            logger.exception("SSO authentication failed")
            return JsonResponse(
                {"error": "Authentication failed"},
                status=500,
            )


class SsoExchangeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if not config.OIDC_ENABLED:
            return Response(
                {"error": "SSO is not enabled"},
                status=status.HTTP_404_NOT_FOUND,
            )

        exchange_code = request.data.get("code", "")
        if not exchange_code:
            return JsonResponse({"error": "Missing exchange code"}, status=400)

        data = cache.get(f"sso_exchange_{exchange_code}")
        if not data:
            return JsonResponse({"error": "Invalid or expired exchange code"}, status=400)

        cache.delete(f"sso_exchange_{exchange_code}")
        return JsonResponse(data)
