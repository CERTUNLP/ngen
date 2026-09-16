import django_filters
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import permissions, filters, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from ngen import models, serializers
from ngen.filters import UserFilter
from ngen.serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    CookieTokenRefreshSerializer,
)
from ngen.permissions import (
    CustomApiViewPermission,
    CustomMethodApiViewPermission,
    CustomModelPermissions,
    IsSelf,
)


def refresh_cookie_path():
    """
    Where the refresh cookie is allowed to travel: the endpoints that hand it
    over, renew it and take it out of circulation, and nowhere else. Naming only
    the one that renews left it out of the logout, which is the endpoint that
    has to read it to revoke it
    """
    return reverse("ctoken-create")


def set_refresh_cookie(response, refresh_token):
    """
    The refresh token is handed over as a cookie the javascript cannot read, and
    the browser only sends it to the endpoints of the session: it is limited to
    that path, to that site and, outside of development, to https.
    """
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path=refresh_cookie_path(),
    )
    return response


def delete_refresh_cookie(response):
    """
    A cookie is only removed by naming the path it was written with
    """
    response.delete_cookie("refresh_token", path=refresh_cookie_path(), samesite="Lax")
    return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.prefetch_related("contacts").all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["username", "email", "first_name", "last_name"]
    filterset_class = UserFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "username",
        "email",
        "priority",
        "first_name",
        "last_name",
    ]
    serializer_class = serializers.UserSerializer
    permission_classes = [CustomModelPermissions]


class UserProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSelf,
        CustomMethodApiViewPermission,
    ]
    required_permissions = {
        "GET": ["ngen.view_userprofile"],
        "HEAD": ["ngen.view_userprofile"],
        "PATCH": ["ngen.change_userprofile"],
        "PUT": ["not_allowed"],
        "POST": ["not_allowed"],
        "DELETE": ["not_allowed"],
    }
    pagination_class = None

    def get_queryset(self):
        # Filtra el queryset para incluir solo el perfil del usuario logueado
        return models.User.objects.filter(id=self.request.user.id)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [CustomModelPermissions]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    permission_classes = [CustomModelPermissions]


class RegisterViewSet(viewsets.ModelViewSet):
    http_method_names = ["post"]
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        if not settings.ALLOW_SIGNUP:
            return Response(
                {"success": False, "msg": "Signup is disabled"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "success": True,
                "userID": user.id,
                "msg": "The user was successfully registered",
            },
            status=status.HTTP_201_CREATED,
        )


class ObtainApiKeyView(ObtainAuthToken):
    """
    The api token is handed over for the same credentials as the login, so it is
    worth the same and is limited the same
    """

    throttle_scope = "login"


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"


class CustomTokenRefreshView(TokenRefreshView):
    """
    The refresh that takes the token in the body instead of the cookie, counted
    the same as the one the frontend uses
    """

    throttle_scope = "token_refresh"


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            set_refresh_cookie(response, response.data["refresh"])
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    """
    Renewing is counted apart from the login: it is not a way of guessing a
    password, it asks for the refresh cookie of a session that already exists,
    and every browser of the deployment comes back here every few minutes
    """

    serializer_class = CookieTokenRefreshSerializer
    throttle_scope = "token_refresh"

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            set_refresh_cookie(response, response.data["refresh"])
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenLogoutView(APIView):
    """
    Closing a session is what takes its refresh token out of circulation, and
    the cookie is what says which session that is: holding it is the proof, the
    same way it is the proof when it asks for a new access token.

    It does not ask for an access token on top. A browser that was left alone
    has an access token that expired minutes ago, and that is exactly when
    somebody closes the session: asking for one meant answering 401 and leaving
    the refresh token alive for the rest of its hour.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        # The cookie is the only credential this asks for, and a browser
        # attaches it to any post of the same site: a form served from another
        # subdomain would be enough to close somebody's session. A header is
        # what says a page of the application is the one asking, because a form
        # cannot add one and anything that can is asked for permission first
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            return Response(
                {"detail": "Missing X-Requested-With header"},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            # Never hand an empty value to simplejwt: with no token it mints a
            # brand new one instead of failing, and blacklisting that one
            # answers as if the session had been closed while the token of the
            # user stays valid until it expires on its own
            return delete_refresh_cookie(
                Response(
                    {"detail": "No refresh token found in cookie 'refresh_token'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            # Expired, or already taken out of circulation by another tab:
            # there is nothing left to revoke and the session is over anyway
            pass

        return delete_refresh_cookie(Response(status=status.HTTP_205_RESET_CONTENT))


class UserMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_user"]


class PermissionMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_permission"]


class GroupMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_group"]
