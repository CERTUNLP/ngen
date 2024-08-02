"""
Django Unit Tests for Event model
"""
import uuid

from django.test import TestCase

from ngen.models import Event, User, Taxonomy, TaxonomyGroup, Feed, Tlp, Priority, \
    CaseTemplate, Playbook, Task, State, Case


class EventTest(TestCase):
    """
    This will handle Event model tests
    """

    @classmethod
    def setUpTestData(cls):
        """
        Event model test setup
        """
        cls.taxonomy_group = TaxonomyGroup.objects.create(
            name="Internal",
            description="First group"
        )
        cls.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        cls.feed = Feed.objects.create(slug="shodan", name="Shodan")
        cls.tlp = Tlp.objects.create(
            slug="white",
            when="Given some circumstance",
            why="Some reason",
            information="Some information",
            description="Some description",
            name="White",
            code=0,
        )
        cls.priority = Priority.objects.create(name="Medium", severity=3)
        cls.user = User.objects.create(
            username="test", password="test", priority=cls.priority
        )
        cls.playbook = Playbook.objects.create(
            name="Test playbook",
        )
        cls.task = Task.objects.create(
            name="Test task",
            description="Test description",
            playbook=cls.playbook,
            priority=cls.priority,
        )
        cls.state = State.objects.create(name="Open")

        cls.case_template = CaseTemplate.objects.create(
            priority=cls.priority,
            cidr=None,
            domain="info.unlp.edu.ar",
            event_taxonomy=cls.taxonomy,
            event_feed=cls.feed,
            case_tlp=cls.tlp,
            case_state=cls.state,
            case_lifecycle="auto_open",
            active=True,
        )

        cls.event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=cls.taxonomy,
            feed=cls.feed,
            tlp=cls.tlp,
            reporter=cls.user,
            notes="Some notes",
            priority=cls.priority,
        )

        cls.event.tasks.add(cls.task)

    def test_event_creation(self):
        """
        This will test Event creation
        """
        self.assertTrue(isinstance(self.event, Event))

    def test_cidr(self):
        """
        This will test Event cidr attribute
        """
        self.assertEqual(self.event.cidr, None)

    def test_domain(self):
        """
        This will test Event domain attribute
        """
        self.assertEqual(self.event.domain, "info.unlp.edu.ar")

    def test_taxonomy(self):
        """
        This will test Event taxonomy attribute
        """
        self.assertEqual(self.event.taxonomy, self.taxonomy)

    def test_feed(self):
        """
        This will test Event feed attribute
        """
        self.assertEqual(self.event.feed, self.feed)

    def test_tlp(self):
        """
        This will test Event tlp attribute
        """
        self.assertEqual(self.event.tlp, self.tlp)

    def test_priority(self):
        """
        This will test Event priority attribute
        """
        self.assertEqual(self.event.priority, self.priority)

    def test_reporter(self):
        """
        This will test Event reporter attribute
        """
        self.assertEqual(self.event.reporter, self.user)

    def test_evidence_file_path(self):
        """
        This will test Event reporter attribute
        """
        self.assertEqual(self.event.evidence_file_path, None)

    def test_notes(self):
        """
        This will test Event notes attribute
        """
        self.assertEqual(self.event.notes, "Some notes")

    def test_node_order_by(self):
        """
        This will test Event node_order_by attribute
        """
        self.assertEqual(self.event.node_order_by, ["id"])

    def test_tasks(self):
        """
        This will test Event taskjs attribute
        """
        self.assertEqual(self.event.tasks.count(), 1)
        self.assertEqual(self.event.tasks.last(), self.task)

    def test_comments(self):
        """
        This will test Event comments attribute
        """
        self.assertEqual(self.event.comments.count(), 0)

    def test_uuid(self):
        """
        This will test Event uuid attribute
        """
        self.assertNotEqual(self.event.uuid, None)
        self.assertTrue(isinstance(self.event.uuid, uuid.UUID))

    def test_case(self):
        """
        This will test Event case attribute,
        given that a Case was created because the Event matched with a Case Template
        """
        case = Case.objects.get(casetemplate_creator=self.case_template)
        self.assertEqual(self.event.case, case)
