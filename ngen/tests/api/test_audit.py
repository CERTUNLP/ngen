from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from auditlog.models import LogEntry

from ngen.models import Priority
from ngen.views.tools import AuditFilter

User = get_user_model()


class TestAuditFilter(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.priority = Priority.objects.create(
            name="Test",
            slug="test",
            severity=10,
        )
        cls.user = User.objects.create_user(
            username="audit_test_user",
            password="test",
            email="audit@test.com",
            priority=cls.priority,
        )
        cls.ct_user = ContentType.objects.get_for_model(User)

    def test_filter_by_model_returns_only_matching_type(self):
        LogEntry.objects.create(
            content_type=self.ct_user,
            object_id="42",
            object_repr="User #42",
            action=0,
            changes={"username": ["", "test"]},
        )
        LogEntry.objects.create(
            content_type=self.ct_user,
            object_id="99",
            object_repr="User #99",
            action=0,
            changes={"username": ["", "other"]},
        )

        filtered = AuditFilter(
            data={"content_type__model": "user", "object_id": "42"},
            queryset=LogEntry.objects.all(),
        )
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first().object_repr, "User #42")

    def test_filter_excludes_other_content_types_same_object_id(self):
        ct_logentry = ContentType.objects.get_for_model(LogEntry)

        LogEntry.objects.create(
            content_type=self.ct_user,
            object_id="42",
            object_repr="User #42",
            action=0,
            changes={},
        )
        LogEntry.objects.create(
            content_type=ct_logentry,
            object_id="42",
            object_repr="LogEntry #42 (same id)",
            action=0,
            changes={},
        )

        filtered = AuditFilter(
            data={"content_type__model": "user", "object_id": "42"},
            queryset=LogEntry.objects.all(),
        )
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first().object_repr, "User #42")

    def test_filter_nonexistent_model_returns_empty(self):
        LogEntry.objects.create(
            content_type=self.ct_user,
            object_id="42",
            object_repr="User #42",
            action=0,
            changes={},
        )

        filtered = AuditFilter(
            data={"content_type__model": "nonexistent", "object_id": "42"},
            queryset=LogEntry.objects.all(),
        )
        self.assertEqual(filtered.qs.count(), 0)

    def test_filter_object_id_only_returns_all_models(self):
        ct_logentry = ContentType.objects.get_for_model(LogEntry)

        LogEntry.objects.create(content_type=self.ct_user, object_id="42", object_repr="User #42", action=0, changes={})
        LogEntry.objects.create(content_type=ct_logentry, object_id="42", object_repr="LogEntry #42", action=0, changes={})

        filtered = AuditFilter(
            data={"object_id": "42"},
            queryset=LogEntry.objects.all(),
        )
        self.assertEqual(filtered.qs.count(), 2)
