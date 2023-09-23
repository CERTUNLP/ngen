# Generated by Django 4.1.10 on 2023-09-23 09:51

import colorfield.fields
import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_bleach.models
import django_lifecycle.mixins
import model_utils.fields
import netfields.fields
import ngen.models.announcement
import ngen.models.case
import ngen.storage
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('api_key', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
            ],
            options={
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Artifact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('type', models.CharField(choices=[('ip', 'IP'), ('domain', 'Domain'), ('fqdn', 'FQDN'), ('url', 'Url'), ('mail', 'Mail'), ('hash', 'Hash'), ('file', 'File'), ('other', 'Other'), ('user-agent', 'User agent'), ('autonomous-system', 'Autonomous system')], default='ip', max_length=20)),
                ('value', models.CharField(default=None, max_length=255)),
            ],
            options={
                'db_table': 'artifact',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('attend_date', models.DateTimeField(null=True)),
                ('solve_date', models.DateTimeField(null=True)),
                ('report_message_id', models.CharField(max_length=255, null=True)),
                ('raw', models.TextField(null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('lifecycle', models.CharField(choices=[('manual', 'Manual'), ('auto', 'Auto'), ('auto_open', 'Auto open'), ('auto_close', 'Auto close')], default='manual', max_length=20)),
                ('notification_count', models.PositiveSmallIntegerField(default=1)),
                ('assigned', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='assigned_cases', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'case',
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model, ngen.models.announcement.Communication),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('public_key', models.CharField(max_length=4000, null=True)),
                ('type', models.CharField(choices=[('email', 'Email'), ('telegram', 'Telegram'), ('phone', 'Phone'), ('uri', 'URI')], default='email', max_length=20)),
                ('role', models.CharField(choices=[('technical', 'Technical'), ('administrative', 'Administrative'), ('abuse', 'Abuse'), ('notifications', 'Notifications'), ('noc', 'NOC')], default='administrative', max_length=20)),
            ],
            options={
                'db_table': 'contact',
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('discr', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'edge',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('cidr', netfields.fields.CidrAddressField(blank=True, default=None, max_length=43, null=True)),
                ('domain', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('address_value', models.CharField(blank=True, default='', max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('evidence_file_path', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, default='', null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='ngen.case')),
            ],
            options={
                'db_table': 'event',
                'ordering': ['-id'],
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, default='', max_length=250, null=True)),
            ],
            options={
                'db_table': 'feed',
            },
        ),
        migrations.CreateModel(
            name='NetworkEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'network_entity',
            },
        ),
        migrations.CreateModel(
            name='Playbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=60)),
            ],
            options={
                'db_table': 'playbook',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('severity', models.IntegerField(unique=True)),
                ('attend_time', models.DurationField(default=datetime.timedelta(days=7))),
                ('solve_time', models.DurationField(default=datetime.timedelta(days=7))),
                ('notification_amount', models.PositiveSmallIntegerField(default=3)),
                ('color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=[('#FFFFFF', 'white'), ('#000000', 'black')])),
            ],
            options={
                'db_table': 'priority',
                'ordering': ['severity'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=140)),
                ('description', models.TextField(null=True)),
                ('playbook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='ngen.playbook')),
                ('priority', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority')),
            ],
            options={
                'db_table': 'task',
                'ordering': ['priority__severity'],
            },
        ),
        migrations.CreateModel(
            name='Tlp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=[('#FFFFFF', 'white'), ('#000000', 'black')])),
                ('when', models.TextField(max_length=500)),
                ('why', models.TextField(max_length=500)),
                ('information', models.TextField(max_length=10)),
                ('description', models.TextField(max_length=150)),
                ('encrypt', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=45)),
                ('code', models.IntegerField()),
            ],
            options={
                'db_table': 'tlp',
            },
        ),
        migrations.CreateModel(
            name='TodoTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('completed', models.BooleanField(default=False)),
                ('completed_date', models.DateTimeField(null=True)),
                ('note', models.TextField(null=True)),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='ngen.event')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='ngen.task')),
            ],
            options={
                'db_table': 'todo_task',
                'ordering': ['task__playbook'],
                'unique_together': {('task', 'event')},
            },
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('type', models.CharField(choices=[('vulnerability', 'Vulnerability'), ('incident', 'Incident')], max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.taxonomy')),
            ],
            options={
                'db_table': 'taxonomy',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('blocked', models.BooleanField(default=False)),
                ('attended', models.BooleanField(default=False)),
                ('solved', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, default='', max_length=250, null=True)),
                ('children', models.ManyToManyField(related_name='parents', through='ngen.Edge', to='ngen.state')),
            ],
            options={
                'db_table': 'state',
            },
        ),
        migrations.AddField(
            model_name='playbook',
            name='taxonomy',
            field=models.ManyToManyField(related_name='playbooks', to='ngen.taxonomy'),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('cidr', netfields.fields.CidrAddressField(blank=True, default=None, max_length=43, null=True)),
                ('domain', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('address_value', models.CharField(blank=True, default='', max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('type', models.CharField(choices=[('internal', 'Internal'), ('external', 'External')], default='internal', max_length=20)),
                ('contacts', models.ManyToManyField(blank=True, to='ngen.contact')),
                ('network_entity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='networks', to='ngen.networkentity')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.network')),
            ],
            options={
                'db_table': 'network',
                'ordering': ['-cidr'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('response', models.JSONField(blank=True, null=True)),
                ('pending', models.IntegerField()),
                ('discr', models.CharField(max_length=255)),
                ('deletedat', models.DateTimeField(blank=True, db_column='deletedAt', null=True)),
                ('case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ngen.case')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'message',
            },
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('file', models.FileField(null=True, storage=ngen.storage.HashedFilenameStorage(), unique=True, upload_to=ngen.models.case.Evidence.directory_path)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'db_table': 'evidence',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='feed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.feed'),
        ),
        migrations.AddField(
            model_name='event',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.event'),
        ),
        migrations.AddField(
            model_name='event',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority'),
        ),
        migrations.AddField(
            model_name='event',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events_reporter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='tasks',
            field=models.ManyToManyField(related_name='events', through='ngen.TodoTask', to='ngen.task'),
        ),
        migrations.AddField(
            model_name='event',
            name='taxonomy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.taxonomy'),
        ),
        migrations.AddField(
            model_name='event',
            name='tlp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.tlp'),
        ),
        migrations.AddField(
            model_name='edge',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents_edge', to='ngen.state'),
        ),
        migrations.AddField(
            model_name='edge',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children_edge', to='ngen.state'),
        ),
        migrations.AddField(
            model_name='contact',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority'),
        ),
        migrations.CreateModel(
            name='CaseTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('cidr', netfields.fields.CidrAddressField(blank=True, default=None, max_length=43, null=True)),
                ('domain', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('address_value', models.CharField(blank=True, default='', max_length=255)),
                ('case_lifecycle', models.CharField(choices=[('manual', 'Manual'), ('auto', 'Auto'), ('auto_open', 'Auto open'), ('auto_close', 'Auto close')], default='auto', max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('case_state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='decision_states', to='ngen.state')),
                ('case_tlp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.tlp')),
                ('event_feed', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.feed')),
                ('event_taxonomy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.taxonomy')),
                ('priority', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority')),
            ],
            options={
                'db_table': 'case_template',
            },
        ),
        migrations.AddField(
            model_name='case',
            name='casetemplate_creator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cases_created', to='ngen.casetemplate'),
        ),
        migrations.AddField(
            model_name='case',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.case'),
        ),
        migrations.AddField(
            model_name='case',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority'),
        ),
        migrations.AddField(
            model_name='case',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cases', to='ngen.state'),
        ),
        migrations.AddField(
            model_name='case',
            name='tlp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.tlp'),
        ),
        migrations.AddField(
            model_name='case',
            name='user_creator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cases_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=255)),
                ('body', django_bleach.models.BleachField(null=True)),
                ('lang', models.CharField(choices=[('en', 'en'), ('es', 'es')], default='en', max_length=2)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.network')),
                ('priority', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority')),
                ('tlp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.tlp')),
            ],
            options={
                'db_table': 'announcement',
            },
            bases=(models.Model, ngen.models.announcement.Communication),
        ),
        migrations.AddField(
            model_name='user',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ngen.priority'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('lang', models.CharField(choices=[('en', 'en'), ('es', 'es')], default='en', max_length=2)),
                ('problem', django_bleach.models.BleachField()),
                ('derived_problem', django_bleach.models.BleachField(null=True)),
                ('verification', django_bleach.models.BleachField(null=True)),
                ('recommendations', django_bleach.models.BleachField(null=True)),
                ('more_information', django_bleach.models.BleachField(null=True)),
                ('taxonomy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='ngen.taxonomy')),
            ],
            options={
                'db_table': 'report',
                'unique_together': {('lang', 'taxonomy')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='edge',
            unique_together={('parent', 'child')},
        ),
        migrations.CreateModel(
            name='ArtifactRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('object_id', models.PositiveIntegerField()),
                ('artifact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artifact_relation', to='ngen.artifact')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artifact_relation', to='contenttypes.contenttype')),
            ],
            options={
                'db_table': 'artifact_relation',
                'unique_together': {('artifact', 'object_id', 'content_type')},
            },
        ),
        migrations.CreateModel(
            name='ArtifactEnrichment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=100)),
                ('success', models.BooleanField(default=True)),
                ('raw', models.JSONField()),
                ('artifact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrichments', to='ngen.artifact')),
            ],
            options={
                'db_table': 'artifact_enrichment',
                'unique_together': {('artifact', 'name')},
            },
        ),
    ]
