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

    @classmethod
    def setUpTestData(cls):
        """
        Case model test setup
        """

        cls.priority = Priority.objects.get(slug="critical")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.state = State.objects.get(slug="open")
        cls.name = 'Test Case'

        cls.template1 = CaseTemplate.objects.create(
            domain="info.unlp.edu.ar",
            priority=Priority.objects.get(slug="critical"),
            event_taxonomy=Taxonomy.objects.get(slug="blacklist"),
            event_feed=Feed.objects.get(slug="csirtamericas"),
            case_tlp=Tlp.objects.get(slug="white"),
            case_state=State.objects.get(slug="staging")
        )
        cls.template2 = CaseTemplate.objects.create(
            domain="alumnos.unlp.edu.ar",
            priority=Priority.objects.get(slug="high"),
            event_taxonomy=Taxonomy.objects.get(slug="botnet"),
            event_feed=Feed.objects.get(slug="bro"),
            case_tlp=Tlp.objects.get(slug="green"),
            case_state=State.objects.get(slug="staging")
        )

        cls.case = Case.objects.create(
            priority=cls.priority,
            tlp=cls.tlp,
            casetemplate_creator=cls.template1,
            state=cls.state,
            name=cls.name
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
