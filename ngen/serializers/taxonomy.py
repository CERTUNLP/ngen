from rest_framework import serializers
from rest_framework.fields import CharField

from ngen import models
from ngen.serializers.common.mixins import AuditSerializerMixin


class TaxonomySerializer(AuditSerializerMixin):
    reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='report-detail'
    )
    playbooks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='playbook-detail'
    )

    class Meta:
        model = models.Taxonomy
        fields = '__all__'
        read_only_fields = ['slug']


class TaxonomyGroupSerializer(AuditSerializerMixin):
    taxonomies = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='taxonomy-detail'
    )

    class Meta:
        model = models.TaxonomyGroup
        fields = '__all__'
        read_only_fields = ['slug']


class ReportSerializer(AuditSerializerMixin):
    problem = CharField(style={'base_template': 'textarea.html', 'rows': 10})
    derived_problem = CharField(
        style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    verification = CharField(
        style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    recommendations = CharField(
        style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    more_information = CharField(
        style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)

    class Meta:
        model = models.Report
        fields = '__all__'


class PlaybookSerializer(AuditSerializerMixin):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )

    class Meta:
        model = models.Playbook
        fields = '__all__'


class TaskSerializer(AuditSerializerMixin):
    class Meta:
        model = models.Task
        fields = '__all__'


class TodoTaskSerializer(AuditSerializerMixin):
    class Meta:
        model = models.TodoTask
        fields = '__all__'
        read_only_fields = ['completed_date', 'task', 'event']


class TaxonomyMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taxonomy
        fields = ['url', 'name']
