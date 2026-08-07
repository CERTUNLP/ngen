import django_filters
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import permissions, filters, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
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


def set_refresh_cookie(response, refresh_token):
    """
    The refresh token is handed over as a cookie the javascript cannot read, and
    it is only ever sent by the frontend to the endpoint that refreshes it: it
    is limited to that path, to that site and, outside of development, to https.
    """
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path=reverse("ctoken-refresh"),
    )
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


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            set_refresh_cookie(response, response.data["refresh"])
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer
    throttle_scope = "login"

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            set_refresh_cookie(response, response.data["refresh"])
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
