from rest_framework import serializers
from rest_framework.fields import CharField

from ngen import models
from ngen.serializers.utils.mixins import NgenModelSerializer


class TaxonomySerializer(NgenModelSerializer):
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


class ReportSerializer(NgenModelSerializer):
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


class PlaybookSerializer(NgenModelSerializer):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )

    class Meta:
        model = models.Playbook
        fields = '__all__'


class TaskSerializer(NgenModelSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'


class TodoTaskSerializer(NgenModelSerializer):
    class Meta:
        model = models.TodoTask
        fields = '__all__'
        read_only_fields = ['completed_date', 'task', 'event']
