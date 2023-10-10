from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission

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
        rep = super(UserSerializer, self).to_representation(obj)
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
