from datetime import datetime, timedelta

import jwt
from colorfield.serializers import ColorField
from comment.models import Comment
from constance import config
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField

from ngen import models
from ngen.models import utils, User, ActiveSession


class GenericRelationField(serializers.RelatedField):
    def to_internal_value(self, data):
        pass

    def to_representation(self, related_list):
        return self.generic_detail_links(related_list)

    def generic_detail_links(self, related_list, request=None):
        links = []
        for related in related_list:
            links.append(self.generic_detail_link(related, request))
        return links

    def generic_detail_link(self, related, request=None):
        view_name = related.__class__.__name__.lower() + '-detail'
        serializer = serializers.HyperlinkedIdentityField(view_name=view_name)
        return serializer.get_url(obj=related, view_name=view_name,
                                  request=self.context.get('request', request),
                                  format=None)


class EvidenceSerializerMixin(serializers.HyperlinkedModelSerializer):

    def update(self, instance, validated_data):
        files = self.context.get('request').FILES
        if files:
            validated_data['files'] = files.getlist('evidence')
        event = super().update(instance, validated_data)
        return event

    def create(self, validated_data):
        files = self.context.get('request').FILES
        if files:
            validated_data['files'] = files.getlist('evidence')
        event = super().create(validated_data)
        return event


class MergeSerializerMixin:
    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action
        if action in ['update', 'partial_update', 'retrieve'] and self.instance and not self.instance.mergeable:
            if self.instance.blocked:
                allowed_fields = self.allowed_fields()
            elif self.instance.merged:
                allowed_fields = []
            for field in self.instance._meta.fields:
                if field.name not in allowed_fields:
                    kwargs = extra_kwargs.get(field.name, {})
                    kwargs['read_only'] = True
                    if field.is_relation:
                        kwargs['queryset'] = None
                    extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate_parent(self, parent: 'utils.NgenMergeableModel'):
        if parent and parent.mergeable_with(self.instance):
            return parent

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance and self.instance.merged:
            raise ValidationError(gettext('Merged instances can\'t be modified'))
        if self.instance and self.instance.blocked:
            allowed_fields = self.allowed_fields()
            for attr in list(attrs):
                if attr not in allowed_fields:
                    if config.ALLOWED_FIELDS_EXCEPTION:
                        raise ValidationError({attr: gettext('%s of blocked instances can\'t be modified') % attr})
                    attrs.pop(attr)
        return attrs

    @staticmethod
    def allowed_fields():
        raise NotImplementedError


class EventSerializer(MergeSerializerMixin, EvidenceSerializerMixin, serializers.HyperlinkedModelSerializer):
    evidence = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='evidence-detail'
    )
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )
    todos = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='todotask-detail'
    )
    artifacts = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='artifact-detail'
    )
    comments = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = '__all__'

    def get_comments(self, obj):
        comments_qs = Comment.objects.filter_parents_by_object(obj)
        return GenericRelationField(read_only=True).generic_detail_links(comments_qs, self.context.get('request'))

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_EVENT.split(',')

    @staticmethod
    def not_allowed_fields():
        return ['taxonomy', 'feed', 'network']

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action
        if action in ['update', 'partial_update', 'retrieve']:
            if self.instance and self.instance.is_parent():
                for field in self.instance._meta.fields:
                    if field.name in self.not_allowed_fields():
                        kwargs = extra_kwargs.get(field.name, {})
                        kwargs['read_only'] = True
                        extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            if self.instance.merged or self.instance.is_parent():
                for attr in list(attrs):
                    if attr in self.not_allowed_fields():
                        if config.ALLOWED_FIELDS_EXCEPTION:
                            raise ValidationError(
                                {attr: gettext('%s of merged events can\'t be modified') % self.not_allowed_fields()})
                        attrs.pop(attr)
        return attrs


class CaseSerializer(MergeSerializerMixin, EvidenceSerializerMixin, serializers.HyperlinkedModelSerializer):
    events = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='case-detail'
    )
    evidence = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = models.Case
        fields = '__all__'
        read_only_fields = ['attend_date', 'solve_date', 'report_message_id', 'raw', 'created_by', 'notification_count']

    def get_evidence(self, obj):
        return GenericRelationField(read_only=True).generic_detail_links(obj.evidence_all, self.context.get('request'))

    def validate_state(self, attrs):
        if self.instance is not None and self.instance.state != attrs and not self.instance.state.is_parent_of(attrs):
            raise ValidationError(
                {'state': gettext(
                    'It\'s not possible to change the state "%s" to "%s". The new possible states are %s') % (
                              self.instance.state, attrs, list(self.instance.state.children.all()))})
        return attrs

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        if self.instance:
            kwargs = extra_kwargs.get('state', {})
            action = self.context['view'].action
            if not kwargs.get('read_only', False):
                if action in ['update', 'partial_update']:
                    queryset = (self.instance.state.children.all() | models.State.objects.filter(
                        pk=self.instance.state.pk)).distinct()
                    kwargs['queryset'] = queryset
                else:
                    kwargs['queryset'] = models.State.get_initial().children.all()
                extra_kwargs['state'] = kwargs
        return extra_kwargs

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_CASE.split(',')

    def get_comments(self, obj):
        comments_qs = Comment.objects.filter_parents_by_object(obj)
        return GenericRelationField(read_only=True).generic_detail_links(comments_qs, self.context.get('request'))


class EvidenceSerializer(serializers.HyperlinkedModelSerializer):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Evidence
        exclude = ['content_type', 'object_id']

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(obj.content_object, self.context.get('request'))


class TaxonomySerializer(serializers.HyperlinkedModelSerializer):
    reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='report-detail'
    )

    class Meta:
        model = models.Taxonomy
        fields = '__all__'


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    problem = CharField(style={'base_template': 'textarea.html', 'rows': 10})
    derived_problem = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    verification = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    recommendations = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    more_information = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)

    class Meta:
        model = models.Report
        fields = '__all__'


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Feed
        fields = '__all__'


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.State
        fields = '__all__'


class EdgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Edge
        fields = '__all__'


class TlpSerializer(serializers.HyperlinkedModelSerializer):
    color = ColorField()

    class Meta:
        model = models.Tlp
        fields = '__all__'


class PrioritySerializer(serializers.HyperlinkedModelSerializer):
    color = ColorField()

    class Meta:
        model = models.Priority
        fields = '__all__'

    def validate(self, attrs):
        if self.instance is not None and not (attrs['solve_time'] > attrs['attend_deadline']):
            raise ValidationError({'solve_time': gettext('The solve time must be greater than attend deadline')})
        return attrs


class CaseTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CaseTemplate
        fields = '__all__'


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='network-detail'
    )

    class Meta:
        model = models.Network
        fields = '__all__'


class NetworkEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.NetworkEntity
        fields = '__all__'


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contact
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.User
        exclude = ['user_permissions', 'password', 'groups']


class PlaybookSerializer(serializers.HyperlinkedModelSerializer):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )

    class Meta:
        model = models.Playbook
        fields = '__all__'


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'


class TodoTaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TodoTask
        fields = '__all__'
        read_only_fields = ['completed_date', 'task', 'event']


class ArtifactSerializer(serializers.HyperlinkedModelSerializer):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Artifact
        fields = '__all__'

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_links(obj.related, self.context.get('request'))


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


def _generate_jwt_token(user):
    token = jwt.encode(
        {"id": user.pk, "exp": datetime.utcnow() + timedelta(days=7)},
        settings.SECRET_KEY,
    )

    return token


class LoginSerializer(serializers.Serializer):
    # email = serializers.CharField(max_length=255)
    # username = serializers.CharField(max_length=255, read_only=True)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email", None)
        username = data.get("username", None)
        password = data.get("password", None)

        if username is None:
            raise exceptions.ValidationError(
                {"success": False, "msg": "Username is required to login"}
            )
        if password is None:
            raise exceptions.ValidationError(
                {"success": False, "msg": "Password is required to log in."}
            )
        user = authenticate(username=username, password=password)

        if user is None:
            raise exceptions.AuthenticationFailed({"success": False, "msg": "Wrong credentials"})

        if not user.is_active:
            raise exceptions.ValidationError(
                {"success": False, "msg": "User is not active"}
            )

        try:
            session = ActiveSession.objects.get(user=user)
            if not session.token:
                raise ValueError

            jwt.decode(session.token, settings.SECRET_KEY, algorithms=["HS256"])

        except (ObjectDoesNotExist, ValueError, jwt.ExpiredSignatureError):
            session = ActiveSession.objects.create(
                user=user, token=_generate_jwt_token(user)
            )

        return {
            "success": True,
            "token": session.token,
            "user": {"_id": user.pk, "username": user.username, "email": user.email},
        }


class AnnouncementSerializer(EvidenceSerializerMixin, serializers.HyperlinkedModelSerializer):
    body = CharField(style={'base_template': 'textarea.html', 'rows': 10})
    evidence = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='evidence-detail'
    )

    class Meta:
        model = models.Announcement
        fields = '__all__'


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Comment
        exclude = ['content_type', 'object_id']
