from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ngen.models import User
from .common.mixins import AuditSerializerMixin


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=4, max_length=128, write_only=True)
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


class UserSerializer(AuditSerializerMixin):
    user_permissions = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='permission-detail',
        read_only=True
    )

    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if 'password' in rep:
            if rep.get('password'):
                rep['password'] = '********'
            else:
                rep['password'] = None
        return rep

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class GroupSerializer(AuditSerializerMixin):
    permissions = serializers.HyperlinkedRelatedField(
        queryset=Permission.objects.prefetch_related('content_type').all(),
        many=True,
        view_name='permission-detail'
    )

    class Meta:
        model = Group
        fields = '__all__'


class PermissionSerializer(AuditSerializerMixin):
    content_type = serializers.HyperlinkedRelatedField(
        queryset=ContentType.objects.all().prefetch_related('permission_set'),
        view_name='contenttype-detail'
    )

    class Meta:
        model = Permission
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data_user = reverse('user-detail', kwargs={'pk': self.user.id}, request=self.context.get('request'))
        data_priority = reverse('priority-detail', kwargs={'pk': self.user.priority.id},
                                request=self.context.get('request'))
        # Get all permissions from groups and user
        perms = Permission.objects.filter(group__in=self.user.groups.all()) | self.user.user_permissions.all()
        perm_serializer = PermissionSerializer(perms, many=True, context={'request': self.context.get('request')})

        data.update({
            'user': {
                'id': self.user.id,
                'url': data_user,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'priority': data_priority,
                'last_login': self.user.last_login,
                'date_joined': self.user.date_joined,
                'is_superuser': self.user.is_superuser,
                'is_staff': self.user.is_staff,
                'permissions': perm_serializer.data,
            }
        })

        return data
