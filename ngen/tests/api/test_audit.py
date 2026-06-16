from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from auditlog.models import LogEntry

from ngen.models import Priority, Tlp, Taxonomy, Feed, Network
from ngen.models.case import Event, Case
from ngen.models.state import State
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


class TestAuditFilterThroughModels(TestCase):
    fixtures = [
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/state.json",
        "tests/feed.json",
        "tests/taxonomy.json",
        "tests/network.json",
        "tests/contact.json",
        "tests/network_entity.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.taxonomy = Taxonomy.objects.get(pk=1)
        cls.feed = Feed.objects.get(pk=1)
        cls.network = Network.objects.get(pk=1)
        cls.user = User.objects.first()

    def _create_event(self):
        return Event.objects.create(
            domain="through-test.unlp.edu.ar",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            network=self.network,
            reporter=self.user,
            priority=self.priority,
        )

    def test_tag_add_creates_audit_entry_for_event(self):
        event = self._create_event()
        event.tags.add("test-tag")

        ct_event = ContentType.objects.get_for_model(Event)
        entries = LogEntry.objects.filter(
            content_type=ct_event, object_id=str(event.pk)
        )
        self.assertGreaterEqual(
            entries.count(), 2,
            f"Expected at least 2 entries (create + tag add), got {entries.count()}"
        )

    def test_filter_includes_taggedobject_for_event(self):
        event = self._create_event()
        event.tags.add("test-tag-2")

        filtered = AuditFilter(
            data={"content_type__model": "event", "object_id": str(event.pk)},
            queryset=LogEntry.objects.all(),
        )
        total = filtered.qs.count()
        self.assertGreaterEqual(
            total, 2,
            f"Expected at least 2 entries via filter, got {total}"
        )

    def test_tag_remove_creates_audit_entry_for_event(self):
        event = self._create_event()
        event.tags.add("test-tag")
        event.tags.remove("test-tag")

        ct_event = ContentType.objects.get_for_model(Event)
        entries = LogEntry.objects.filter(
            content_type=ct_event, object_id=str(event.pk)
        )
        tag_entries = entries.filter(changes__icontains="removed")
        self.assertGreaterEqual(
            tag_entries.count(), 1,
            f"Expected at least 1 'removed' entry, got {tag_entries.count()}"
        )
