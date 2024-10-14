from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from ngen.models import User
from .common.mixins import AuditSerializerMixin


def password_validation(password):
    if (
        len(password) < 8
        or password.isdigit()
        or password.isalpha()
        or password.islower()
        or password.isupper()
        or password.isalnum()
    ):
        raise serializers.ValidationError(
            "Password must be at least 8 characters long, contain at least one letter, contain at least one number, contain at least one uppercase letter, contain at least one lowercase letter, contain at least one special character"
        )
    return password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=4, max_length=128, write_only=True)
    username = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "is_active"]

    def create(self, validated_data):

        try:
            User.objects.get(email=validated_data["email"])
        except ObjectDoesNotExist:
            return User.objects.create_user(**validated_data)

        raise ValidationError({"success": False, "msg": "Email already taken"})


class UserSerializer(serializers.HyperlinkedModelSerializer):
    history = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "url",
            "history",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "is_staff",
            "is_network_admin",
            "is_active",
            "date_joined",
            "created",
            "modified",
            "api_key",
            "priority",
            "groups",
            "user_permissions",
        ]

    def get_history(self, obj):
        return reverse(
            "user-logentry-list",
            kwargs={"pk": obj.id},
            request=self.context.get("request"),
        )

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if "password" in rep:
            if rep.get("password"):
                rep["password"] = "********"
            else:
                rep["password"] = None
        return rep

    def create(self, validated_data):
        groups_data = validated_data.pop("groups", None)
        permissions_data = validated_data.pop("user_permissions", None)
        password = validated_data.pop("password", None)

        instance = self.Meta.model(**validated_data)

        if password:
            password_validation(password)
            instance.set_password(password)

        instance.save()

        if permissions_data is not None:
            instance.user_permissions.set(permissions_data)

        if groups_data is not None:
            instance.groups.set(groups_data)

        return instance

    def update(self, instance, validated_data):
        groups_data = validated_data.pop("groups", None)
        permissions_data = validated_data.pop("user_permissions", None)

        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            password_validation(password)
            instance.set_password(password)

        # Update permissions
        if permissions_data is not None:
            instance.user_permissions.set(permissions_data)

        # Update groups
        if groups_data is not None:
            instance.groups.set(groups_data)

        instance.save()
        return instance


class UserProfileSerializer(AuditSerializerMixin):
    old_password = serializers.CharField(
        max_length=128, write_only=True, required=False
    )
    new_password1 = serializers.CharField(
        max_length=128, write_only=True, required=False
    )
    new_password2 = serializers.CharField(
        max_length=128, write_only=True, required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_network_admin",
            "is_superuser",
            "date_joined",
            "last_login",
            "priority",
            "groups",
            "user_permissions",
            "old_password",
            "new_password1",
            "new_password2",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_network_admin",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "new_password1": {"write_only": True},
            "new_password2": {"write_only": True},
            "old_password": {"write_only": True},
        }

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("The password you entered is invalid.")
        return value

    def validate_new_password1(self, value):
        if not "old_password" in self.initial_data:
            raise serializers.ValidationError("Old password field is required.")
        if self.instance.check_password(value):
            raise serializers.ValidationError(
                "The new password must be different from the old one."
            )
        password_validation(value)
        return value

    def validate_new_password2(self, value):
        if self.initial_data["new_password1"] != value:
            raise serializers.ValidationError("The two password fields didn’t match.")
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "new_password1":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class GroupSerializer(AuditSerializerMixin):
    permissions = serializers.HyperlinkedRelatedField(
        queryset=Permission.objects.prefetch_related("content_type").all(),
        many=True,
        view_name="permission-detail",
    )

    class Meta:
        model = Group
        fields = "__all__"


class GroupMinifiedSerializer(AuditSerializerMixin):
    class Meta:
        model = Group
        fields = ["url", "name"]
        read_only_fields = ["url"]


class PermissionSerializer(AuditSerializerMixin):
    content_type = serializers.HyperlinkedRelatedField(
        queryset=ContentType.objects.all().prefetch_related("permission_set"),
        view_name="contenttype-detail",
    )

    class Meta:
        model = Permission
        fields = "__all__"


class UserMinifiedSerializer(AuditSerializerMixin):
    class Meta:
        model = User
        fields = ["url", "username"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data_user = reverse(
            "user-detail",
            kwargs={"pk": self.user.id},
            request=self.context.get("request"),
        )
        data_priority = reverse(
            "priority-detail",
            kwargs={"pk": self.user.priority.id},
            request=self.context.get("request"),
        )
        # Get all permissions from groups and user
        perms = (
            Permission.objects.filter(group__in=self.user.groups.all())
            | self.user.user_permissions.all()
        )
        perms = {p.codename for p in perms.distinct()}

        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "url": data_user,
                    "email": self.user.email,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "priority": data_priority,
                    "last_login": self.user.last_login,
                    "date_joined": self.user.date_joined,
                    "is_superuser": self.user.is_superuser,
                    "is_staff": self.user.is_staff,
                    "permissions": perms,
                    "is_network_admin": self.user.is_network_admin,
                }
            }
        )

        return data


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get("refresh_token")
        if attrs["refresh"]:
            return super().validate(attrs)
        else:
            raise InvalidToken("No valid token found in cookie 'refresh_token'")
