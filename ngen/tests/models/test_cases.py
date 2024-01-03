"""
Django Unit Tests for Case model
"""
from django.test import TestCase

from ngen.models import Tlp, Priority, CaseTemplate, State, Case


class CaseTest(TestCase):
    """
    This will handle Event model tests
    """

    fixtures = ["priority.json", "tlp.json", "user.json", "state.json",
                "feed.json", "taxonomy.json", "case_template.json"
                ]

    def setUp(self):
        """
        Case model test setup
        """

        self.priority = Priority.objects.get(slug="critical")
        self.tlp = Tlp.objects.get(slug="green")
        self.state = State.objects.get(slug="open")
        self.case_template = CaseTemplate.objects.get(pk=1)

        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state
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
        self.assertEqual(self.case.casetemplate_creator, self.case_template)

    def test_state(self):
        """
        This will test Case state attribute
        """
        self.assertEqual(self.case.state, self.state)
