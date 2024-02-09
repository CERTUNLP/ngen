"""
Django Unit Tests for Case model
"""
from django.test import TestCase

from ngen.models import Tlp, Priority, CaseTemplate, State, Case, Taxonomy, Feed


class CaseTest(TestCase):
    """
    This will handle Event model tests
    """

    fixtures = ["priority.json", "tlp.json", "user.json", "state.json",
                "feed.json", "taxonomy.json"]

    def setUp(self):
        """
        Case model test setup
        """

        self.priority = Priority.objects.get(slug="critical")
        self.tlp = Tlp.objects.get(slug="green")
        self.state = State.objects.get(slug="open")
        self.name = 'Test Case'

        self.template1 = CaseTemplate.objects.create(
            domain="info.unlp.edu.ar",
            priority=Priority.objects.get(slug="critical"),
            event_taxonomy=Taxonomy.objects.get(slug="blacklist"),
            event_feed=Feed.objects.get(slug="csirtamericas"),
            case_tlp=Tlp.objects.get(slug="white"),
            case_state=State.objects.get(slug="staging")
        )
        self.template2 = CaseTemplate.objects.create(
            domain="alumnos.unlp.edu.ar",
            priority=Priority.objects.get(slug="high"),
            event_taxonomy=Taxonomy.objects.get(slug="botnet"),
            event_feed=Feed.objects.get(slug="bro"),
            case_tlp=Tlp.objects.get(slug="green"),
            case_state=State.objects.get(slug="staging")
        )

        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.template1,
            state=self.state,
            name=self.name
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
                case_tlp=Tlp.objects.get(slug="white"),
                case_state=State.objects.get(slug="staging")
            )
