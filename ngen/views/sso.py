import json
import urllib.parse
from urllib.parse import urlencode

import jwt as pyjwt
import requests
from constance import config
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class SsoLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not config.OIDC_ENABLED:
            return Response(
                {"error": "SSO is not enabled"},
                status=status.HTTP_404_NOT_FOUND,
            )

        redirect_uri = request.build_absolute_uri(reverse("sso-callback"))
        params = {
            "response_type": "code",
            "client_id": config.OIDC_RP_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": config.OIDC_RP_SCOPES,
            "state": request.GET.get("next", config.OIDC_REDIRECT_URL),
        }
        auth_url = f"{config.OIDC_OP_AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
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

    def _verify_id_token(self, id_token, jwks_data):
        unverified_header = pyjwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")

        signing_key = None
        for key_data in jwks_data.get("keys", []):
            if key_data.get("kid") == kid:
                signing_key = pyjwt.algorithms.RSAAlgorithm.from_jwk(
                    json.dumps(key_data)
                )
                break

        if signing_key is None:
            raise ValueError(f"No matching JWK found for kid: {kid}")

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
        state = request.GET.get("state", config.OIDC_REDIRECT_URL)

        if not code:
            return JsonResponse(
                {"error": "Authorization code not provided"},
                status=400,
            )

        try:
            redirect_uri = request.build_absolute_uri(reverse("sso-callback"))

            token_data = self._exchange_code(code, redirect_uri)
            id_token = token_data.get("id_token", "")

            if not id_token:
                return JsonResponse(
                    {"error": "No ID token received from provider"},
                    status=400,
                )

            jwks_data = self._get_jwks()
            claims = self._verify_id_token(id_token, jwks_data)

            email = claims.get("email", "")
            if not email:
                return JsonResponse(
                    {"error": "Email claim missing in ID token"},
                    status=400,
                )

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
                    {"error": "Could not authenticate user"},
                    status=400,
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

            encoded_user = urllib.parse.quote(json.dumps(user_data))
            encoded_token = urllib.parse.quote(access_jwt)

            frontend_url = config.OIDC_REDIRECT_URL.rstrip("/")
            next_url = (
                state
                if url_has_allowed_host_and_scheme(state, allowed_hosts=None)
                else frontend_url
            )

            redirect_url = (
                f"{frontend_url}/sso-callback"
                f"?access={encoded_token}"
                f"&user={encoded_user}"
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

        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"Failed to connect to OIDC provider: {str(e)}"},
                status=502,
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"SSO authentication failed: {str(e)}"},
                status=500,
            )
