"""
Django Unit Tests for Case model
"""

from unittest.mock import patch

from django.test import TestCase

from ngen.models import Tlp, Priority, CaseTemplate, State, Case, Taxonomy, Feed


class CaseTest(TestCase):
    """
    This will handle Event model tests
    """

    fixtures = [
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/feed.json",
        "tests/taxonomy.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """
        Case model test setup
        """

        cls.priority = Priority.objects.get(slug="critical")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.state = State.objects.get(slug="open")
        cls.name = "Test Case"
        cls.lifecycle = "manual"

        cls.template1 = CaseTemplate.objects.create(
            domain="info.unlp.edu.ar",
            event_taxonomy=Taxonomy.objects.get(slug="blacklist"),
            event_feed=Feed.objects.get(slug="csirtamericas"),
            case_tlp=Tlp.objects.get(slug="clear"),
            case_state=State.objects.get(slug="staging"),
            case_priority=Priority.objects.get(slug="critical"),
        )
        cls.template2 = CaseTemplate.objects.create(
            domain="alumnos.unlp.edu.ar",
            event_taxonomy=Taxonomy.objects.get(slug="botnet"),
            event_feed=Feed.objects.get(slug="bro"),
            case_tlp=Tlp.objects.get(slug="green"),
            case_state=State.objects.get(slug="staging"),
            case_priority=Priority.objects.get(slug="high"),
        )

        cls.case = Case.objects.create(
            priority=cls.priority,
            tlp=cls.tlp,
            casetemplate_creator=cls.template1,
            state=cls.state,
            name=cls.name,
        )

    def test_case_creation(self):
        """
        This will test Case creation
        """
        self.assertTrue(isinstance(self.case, Case))

    def test_priority(self):
        """
        This will test Case priority attribute
        """
        self.assertEqual(self.case.priority, self.priority)

    def test_tlp(self):
        """
        This will test Case tlp attribute
        """
        self.assertEqual(self.case.tlp, self.tlp)

    def test_casetemplate_creator(self):
        """
        This will test Case casetemplate_creator attribute
        """
        self.assertEqual(self.case.casetemplate_creator, self.template1)

    def test_state(self):
        """
        This will test Case state attribute
        """
        self.assertEqual(self.case.state, self.state)

    def test_name(self):
        """
        This will test Case name attribute
        """
        self.assertEqual(self.case.name, self.name)

    def test_lifecycle(self):
        """
        This will test Case lifecycle attribute
        """
        self.assertEqual(self.case.lifecycle, self.lifecycle)

    def validate_unique_case_tempalte(self):
        """
        This will test Case casetemplate_creator attribute
        """
        with self.assertRaises(Exception):
            CaseTemplate.objects.create(
                domain="info.unlp.edu.ar",
                priority=Priority.objects.get(slug="critical"),
                event_taxonomy=Taxonomy.objects.get(slug="blacklist"),
                event_feed=Feed.objects.get(slug="csirtamericas"),
                case_tlp=Tlp.objects.get(slug="clear"),
                case_state=State.objects.get(slug="staging"),
            )

    def test_auto_close_sets_was_auto_closed_flag(self):
        """
        Transitioning a case to a solved state with _auto_closed=True
        must persist was_auto_closed=True in the DB.
        """
        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            state=State.objects.get(slug="open"),  # attended=True, solved=False
        )
        closed_state = State.objects.get(slug="closed")

        with patch.object(Case, "communicate_auto_close") as mock_auto_close, \
             patch.object(Case, "communicate_close") as mock_close:
            case._auto_closed = True
            case.was_auto_closed = True
            case.state = closed_state
            case.save()

        case.refresh_from_db()
        self.assertTrue(case.was_auto_closed)

    def test_auto_close_calls_communicate_auto_close_not_communicate_close(self):
        """
        When _auto_closed=True, the auto-close communication template must be
        used instead of the regular close template.
        """
        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            state=State.objects.get(slug="open"),
        )
        closed_state = State.objects.get(slug="closed")

        with patch.object(Case, "communicate_auto_close") as mock_auto_close, \
             patch.object(Case, "communicate_close") as mock_close:
            case._auto_closed = True
            case.was_auto_closed = True
            case.state = closed_state
            case.save()

            mock_auto_close.assert_called_once()
            mock_close.assert_not_called()

    def test_manual_close_does_not_set_was_auto_closed(self):
        """
        A regular (non-auto) close must leave was_auto_closed=False.
        """
        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            state=State.objects.get(slug="open"),
        )
        closed_state = State.objects.get(slug="closed")

        with patch.object(Case, "communicate_close"), \
             patch.object(Case, "communicate_auto_close"):
            case.state = closed_state
            case.save()

        case.refresh_from_db()
        self.assertFalse(case.was_auto_closed)

    def test_communicate_v2_increments_notification_count(self):
        """
        communicate_v2() must atomically increment notification_count by 1.
        """
        with patch.object(Case, "communicate_affected"), \
             patch.object(Case, "communicate_intern"):
            case = Case.objects.create(
                priority=self.priority,
                tlp=self.tlp,
                state=self.state,
            )
            count_before = case.notification_count
            case.communicate_v2("case_report")

        case.refresh_from_db()
        self.assertEqual(case.notification_count, count_before + 1)

    def test_communicate_v2_increments_notification_count_multiple_times(self):
        """
        Calling communicate_v2() N times must result in notification_count == initial + N.
        """
        with patch.object(Case, "communicate_affected"), \
             patch.object(Case, "communicate_intern"):
            case = Case.objects.create(
                priority=self.priority,
                tlp=self.tlp,
                state=self.state,
            )
            count_before = case.notification_count
            for _ in range(3):
                case.communicate_v2("case_report")

        case.refresh_from_db()
        self.assertEqual(case.notification_count, count_before + 3)
