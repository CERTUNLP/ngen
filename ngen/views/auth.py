import django_filters
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import permissions, filters, status, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from ngen import models, serializers
from ngen.filters import UserFilter
from ngen.serializers import RegisterSerializer, CustomTokenObtainPairSerializer, CookieTokenRefreshSerializer


class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permite el acceso solo si el usuario autenticado es el mismo que el objeto
        return obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all().order_by('id')
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_class = UserFilter
    ordering_fields = ['id', 'created', 'modified',
                       'username', 'email', 'priority', 'first_name', 'last_name']
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated, IsSelf]
    pagination_class = None

    def get_queryset(self):
        # Filtra el queryset para incluir solo el perfil del usuario logueado
        return models.User.objects.filter(id=self.request.user.id)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer


class RegisterViewSet(viewsets.ModelViewSet):
    http_method_names = ["post"]
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
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


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

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


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True,
                                path=reverse('ctoken-refresh'))
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True,
                                path=reverse('ctoken-refresh'))
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserMinifiedSerializer
    pagination_class = None
