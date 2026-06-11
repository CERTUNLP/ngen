from gettext import translation

from constance.test import override_config
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils.translation import gettext_lazy
from django.utils import timezone
from django.core import mail
from unittest.mock import patch

from ngen.models.announcement import Communication

from ngen import tasks
from ngen.models import (
    Evidence,
    ContentType,
    Tlp,
    Priority,
    Taxonomy,
    Event,
    Feed,
    State,
    Case,
    CaseTemplate,
    User,
    Contact,
    Task,
    Playbook,
    Network,
    NetworkEntity,
)
from ngen.models.email_message import EmailMessage
from ngen.tests.test_helpers import use_test_email_env


class AnnouncementTestCase(TestCase):
    fixtures = [
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/feed.json",
        "tests/taxonomy.json",
        "tests/case_template.json",
        "tests/contact.json",
        "tests/network_entity.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """SetUp for case and event creation in the tests"""
        cls.priority = Priority.objects.get(name="High")
        cls.tlp = Tlp.objects.get(name="Green")
        cls.state = State.objects.get(name="Open")
        cls.case_template = CaseTemplate.objects.get(pk=1)  # Missing
        cls.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        cls.feed = Feed.objects.get(slug="shodan", name="Shodan")
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

        cls.domain = "unlp.edu.ar"
        cls.subdomain = "info.unlp.edu.ar"
        cls.contact = Contact.objects.get(pk=1)
        cls.network_entity = NetworkEntity.objects.get(pk=1)

        cls.network = Network.objects.create(
            domain=cls.domain,
            active=True,
            type="internal",
            network_entity=cls.network_entity,
        )
        cls.network.contacts.set([cls.contact])

    # ------------------------------CASE-TESTS------------------------------------------

    # ---------------------------------INITIAL------------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_initial(self):
        """
        Creating case: INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,  # High
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial"),
        )

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------STAGING------------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_staging(self):
        """
        Creating case: STAGING. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,  # High
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging"),
        )

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------OPEN---------------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_open(self):
        """
        Creating case: OPEN. Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open"),
        )

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn("open", intern_channel.get_last_message().body.lower())

    # ---------------------------------CLOSED-------------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_closed(self):
        """
        Creating case: CLOSED. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed"),
        )

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------INITIAL-INITIAL----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_initial_initial(self):
        """
        Creating a case: INITIAL > INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial"),
        )
        self.case.state = State.objects.get(name="Initial")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------INITIAL-STAGING----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_initial_staging(self):
        """
        Creating a case: INITIAL > STAGING. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial"),
        )
        self.case.state = State.objects.get(name="Staging")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------INITIAL-OPEN-------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_initial_open(self):
        """
        Creating a case: INITIAL > OPEN. Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial"),
        )
        self.case.state = State.objects.get(name="Open")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn("open", intern_channel.get_last_message().body.lower())

    # ---------------------------------INITIAL-CLOSED-----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_initial_closed(self):
        """
        Creating a case: INITIAL > CLOSED. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial"),
        )
        self.case.state = State.objects.get(name="Closed")
        self.case.state.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------STAGING-INITIAL----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_staging_initial(self):
        """
        Creating a case: STAGING > INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging"),
        )
        self.case.state = State.objects.get(name="Initial")
        self.case.state.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------STAGING-STAGING----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_staging_staging(self):
        """
        Creating a case: STAGING > STAGING. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging"),
        )
        self.case.state = State.objects.get(name="Staging")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------STAGING-OPEN-------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_staging_open(self):
        """
        Creating a case: STAGING > OPEN. Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging"),
        )
        self.case.state = State.objects.get(name="Open")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn("open", intern_channel.get_last_message().body.lower())

    # ---------------------------------STAGING-CLOSED-----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_staging_closed(self):
        """
        Creating a case: STAGING > CLOSED. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging"),
        )
        self.case.state = State.objects.get(name="Closed")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------OPEN-INITIAL-------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_open_initial(self):
        """
        Creating a case: open > initial. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open"),
        )
        self.case.state = State.objects.get(name="Initial")
        self.case.state.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        # Just the mail from Open case
        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn("open", intern_channel.get_last_message().body.lower())

    # ---------------------------------OPEN-STAGING-------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_open_staging(self):
        """
        Creating a case: open > staging. Not possible
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open"),
        )
        self.case.state = State.objects.get(name="Staging")
        self.case.state.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        # Just the mail from Open case
        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn("open", intern_channel.get_last_message().body.lower())

    # ---------------------------------OPEN-OPEN----------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_open_open(self):
        """
        Creating a case: open > open. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open"),
        )
        self.case.state = State.objects.get(name="Open")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        # Just the mail from Open case created
        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn("open", intern_channel.get_last_message().body.lower())

    # ---------------------------------OPEN-CLOSED--------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_open_closed(self):
        """
        Creating a case: open > closed. Mail: Case closed
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open"),
        )
        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)

        self.case.state = State.objects.get(name="Closed")
        self.case.save()

        self.assertEqual(len(intern_channel.get_messages()), 2)
        self.assertIn("Re: ", intern_channel.get_last_message().subject)

    # ---------------------------------CLOSED-INITIAL-----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_closed_initial(self):
        """
        Creating a case: closed > Initial. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed"),
        )
        self.case.state = State.objects.get(name="Initial")
        self.case.state.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------CLOSED-STAGING-----------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_closed_staging(self):
        """
        Creating a case: closed > Staging . Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed"),
        )
        self.case.state = State.objects.get(name="Staging")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn(
            str(gettext_lazy("Case status updated")),
            intern_channel.get_last_message().body,
        )

    # ---------------------------------CLOSED-OPEN--------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_closed_open(self):
        """
        Creating a case: closed > . Not possible.
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed"),
        )
        self.case.state = State.objects.get(name="Open")
        self.case.state.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ---------------------------------CLOSED-CLOSED------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=False)
    def test_case_closed_closed(self):
        """
        Creating a case: closed > . Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed"),
        )
        self.case.state = State.objects.get(name="Closed")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNone(intern_channel)

    # ----------------------------------------------------------------------------------

    # -------------------------------EVENT-TESTS----------------------------------------

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_template_email(self):
        """
        Creating case template and coinciding event. Testing correct case integration and email sending, as well as attachments.
        """
        self.case_template = CaseTemplate.objects.create(
            case_priority=self.priority,
            cidr=None,
            domain=self.domain,
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=State.objects.get(name="Open"),
            case_lifecycle="auto_open",
            active=True,
        )
        self.event = Event.objects.create(
            domain=self.subdomain,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )
        evidence_file = SimpleUploadedFile(
            "file.txt", b"file_content", content_type="text/plain"
        )

        evidence = Evidence.objects.create(
            file=evidence_file,
            object_id=self.event.id,
            content_type=ContentType.objects.get_for_model(Event),
        )

        last_case = Case.objects.order_by("-id").first()

        intern_channel = last_case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        affected_channel = self.event.communication_channels.filter(
            communication_types__type="affected"
        ).first()

        self.assertEqual(last_case, self.event.case)

        # Assert email was sent in intern channel
        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 2)
        self.assertIn("open", intern_channel.get_messages()[0].body.lower())
        self.assertIn("team", intern_channel.get_messages()[1].body.lower())

        # Assert email was sent in affected channel
        self.assertIsNotNone(affected_channel)
        self.assertEqual(len(affected_channel.get_messages()), 2)
        self.assertIn("open", affected_channel.get_messages()[0].body.lower())
        self.assertIn("team", affected_channel.get_messages()[1].body.lower())

        expected_evidence_name = (
            f"Event({self.event.uuid})_{self.event.created.date()}_{evidence.filename}"
        )

        self.assertEqual(evidence.attachment_name, expected_evidence_name)

        # Assert channelable attachments
        self.assertEqual(len(intern_channel.channelable.email_attachments), 1)

        self.assertEqual(
            intern_channel.channelable.email_attachments[0]["name"],
            expected_evidence_name,
        )
        self.assertEqual(len(affected_channel.channelable.email_attachments), 1)
        self.assertEqual(
            affected_channel.channelable.email_attachments[0]["name"],
            expected_evidence_name,
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    def test_case_template_email_with_assigned_name(self):
        """
        Creating case template and coinciding event. Testing correct case integration and email sending, as well as attachments.
        """
        self.case_template = CaseTemplate.objects.create(
            cidr=None,
            domain=self.domain,
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=State.objects.get(name="Open"),
            case_lifecycle="auto_open",
            case_priority=self.priority,
            active=True,
        )
        self.event = Event.objects.create(
            domain=self.subdomain,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

        evidence_file = SimpleUploadedFile(
            "file.txt", b"file_content", content_type="text/plain"
        )

        evidence = Evidence.objects.create(
            file=evidence_file,
            object_id=self.event.id,
            content_type=ContentType.objects.get_for_model(Event),
            assigned_name="EjemploEvidenciá_test-1.archivo_adjunto.txt",
        )

        last_case = Case.objects.order_by("-id").first()

        intern_channel = last_case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        affected_channel = self.event.communication_channels.filter(
            communication_types__type="affected"
        ).first()

        self.assertEqual(last_case, self.event.case)

        # Assert email was sent in intern channel
        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 2)
        self.assertIn("open", intern_channel.get_messages()[0].body.lower())
        self.assertIn("team", intern_channel.get_messages()[1].body.lower())

        # Assert email was sent in affected channel
        self.assertIsNotNone(affected_channel)
        self.assertEqual(len(affected_channel.get_messages()), 2)
        self.assertIn("open", affected_channel.get_messages()[0].body.lower())
        self.assertIn("team", affected_channel.get_messages()[1].body.lower())

        expected_evidence_name = f"Event({self.event.uuid})_{self.event.created.date()}_EjemploEvidenciá-test-1_{evidence.filename}"

        self.assertEqual(evidence.attachment_name, expected_evidence_name)

        # Assert channelable attachments
        self.assertEqual(len(intern_channel.channelable.email_attachments), 1)
        self.assertEqual(
            intern_channel.channelable.email_attachments[0]["name"],
            expected_evidence_name,
        )
        self.assertEqual(len(affected_channel.channelable.email_attachments), 1)
        self.assertEqual(
            affected_channel.channelable.email_attachments[0]["name"],
            expected_evidence_name,
        )

    # ----------------------------------------------------------------------------------
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_config(TEAM_EMAIL="team@ngen.com")
    def test_event_contact(self):
        """
        Creating case template and coinciding event using a network with contacts.
        """
        # Assigning new_contact to the domain test.com
        new_contact = Contact(
            name="Test",
            username="test_contact@example.com",
            public_key="...",
            type=Contact.TYPE.email,
            role=Contact.ROLE.technical,
        )
        new_contact.save()

        self.example_entity = NetworkEntity.objects.create(name="Example Entity")
        network_test = Network.objects.create(
            domain="test.com", network_entity=self.example_entity
        )
        network_test.contacts.set([new_contact])

        # Creating new case template + event
        self.case_template = CaseTemplate.objects.create(
            case_priority=self.priority,
            cidr=None,
            domain="test.com",
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=State.objects.get(name="Open"),
            case_lifecycle="auto_open",
            active=True,
        )
        self.event = Event.objects.create(
            domain="test.com",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )
        # Taking the last created case, making sure it's the one just created, and asserting that the emails are sent to the correct recipients.
        last_case = Case.objects.order_by("-id").first()

        intern_channel = last_case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        affected_channel = self.event.communication_channels.filter(
            communication_types__type="affected"
        ).first()

        self.assertEqual(last_case, self.event.case)

        # Assert email is sent to the contacts.
        self.assertIsNotNone(affected_channel)
        self.assertEqual(len(affected_channel.get_messages()), 1)
        self.assertEqual(
            new_contact.username,
            affected_channel.get_last_message().recipients[0]["email"],
        )

        # Assert email is sent to team email
        self.assertIsNotNone(intern_channel)
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertEqual(
            "team@ngen.com",
            intern_channel.get_last_message().recipients[0]["email"],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_config(TEAM_EMAIL="team@ngen.com")
    def test_2event_case(self):
        """
        Creating two events with different set contacts, then testing correct email sending.
        """
        # First, creating test contacts.
        new_contactA = Contact(
            name="A",
            username="test_A@example.com",
            public_key="...",
            type=Contact.TYPE.email,
            role=Contact.ROLE.technical,
        )
        new_contactA.save()
        new_contactB = Contact(
            name="B",
            username="test_B@example.com",
            public_key="...",
            type=Contact.TYPE.email,
            role=Contact.ROLE.technical,
        )
        new_contactB.save()

        new_contactC = Contact(
            name="C",
            username="test_C@example.com",
            public_key="...",
            type=Contact.TYPE.email,
            role=Contact.ROLE.technical,
        )
        new_contactC.save()

        new_contactD = Contact(
            name="D",
            username="test_D@example.com",
            public_key="...",
            type=Contact.TYPE.email,
            role=Contact.ROLE.technical,
        )
        new_contactD.save()

        # Adding the contacts to a list for later testing purposes
        contact_list1 = [
            "test_A@example.com",
            "test_B@example.com",
            "test_C@example.com",
        ]
        contact_list2 = ["test_D@example.com"]

        # Linking contacts to networks

        self.example_entity = NetworkEntity.objects.create(name="Example Entity")

        network_test1 = Network.objects.create(
            domain="test1.com", network_entity=self.example_entity
        )
        network_test1.contacts.set([new_contactA, new_contactB, new_contactC])

        network_test2 = Network.objects.create(
            domain="test2.com", network_entity=self.example_entity
        )
        network_test2.contacts.set([new_contactD])

        # Case and event creation

        self.case_template = CaseTemplate.objects.create(
            case_priority=self.priority,
            cidr=None,
            domain="test1.com",
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=State.objects.get(name="Open"),
            case_lifecycle="auto_open",
            active=True,
        )
        self.case_template = CaseTemplate.objects.create(
            case_priority=self.priority,
            cidr=None,
            domain="test2.com",
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=State.objects.get(name="Open"),
            case_lifecycle="auto_open",
            active=True,
        )
        self.event_1 = Event.objects.create(
            domain="test1.com",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )
        self.event_2 = Event.objects.create(
            domain="test2.com",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

        intern_channel_1 = self.event_1.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        intern_channel_2 = self.event_2.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        affected_channel_1 = self.event_1.communication_channels.filter(
            communication_types__type="affected"
        ).first()

        affected_channel_2 = self.event_2.communication_channels.filter(
            communication_types__type="affected"
        ).first()

        self.assertIsNotNone(affected_channel_1)
        self.assertEqual(len(affected_channel_1.get_messages()), 1)
        recipient_emails = [
            recipient["email"]
            for recipient in affected_channel_1.get_last_message().recipients
        ]
        self.assertEqual(recipient_emails, contact_list1)

        self.assertIsNotNone(affected_channel_2)
        self.assertEqual(len(affected_channel_2.get_messages()), 1)
        recipient_emails = [
            recipient["email"]
            for recipient in affected_channel_2.get_last_message().recipients
        ]
        self.assertEqual(recipient_emails, contact_list2)

        self.assertIsNotNone(intern_channel_1)
        self.assertEqual(len(intern_channel_1.get_messages()), 1)
        self.assertEqual(
            "team@ngen.com",
            intern_channel_1.get_last_message().recipients[0]["email"],
        )

        self.assertIsNotNone(intern_channel_2)
        self.assertEqual(len(intern_channel_2.get_messages()), 1)
        self.assertEqual(
            "team@ngen.com",
            intern_channel_2.get_last_message().recipients[0]["email"],
        )

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=True)
    def test_summary_emailbackend(self, mock_backend):
        """
        Send summary email with the correct information.

        Checks directly the content of the email sent, as well as the subject and the recipient.
        """
        from django.utils import translation

        translation.activate("en")
        self.addCleanup(translation.deactivate)

        from django.core.mail import get_connection

        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        # Create first event and assign to case
        event1 = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            notes="event1 notes",
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event1.save()
        case = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case.save()

        # Assign event to case
        event1.case = case
        event1.save()

        # Create second event and assign to case
        event2 = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            notes="event2 notes",
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event2.case = case
        event2.save()
        case.save()

        # Close case
        case.state = State.objects.get(slug="closed")
        case.save()

        # basic contact summary test
        tasks.contact_summary.delay(contact_usernames=["soporte@cert.unlp.edu.ar"])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary", status="sent").count(), 1)

        email = mail.outbox[0]

        self.assertEqual(email.subject, "[TEAM][TLP:RED] Summary")
        self.assertEqual(email.to, ["soporte@cert.unlp.edu.ar"])

        self.assertIn("Solved cases: 1", email.body)

        ev1_id = str(event1.uuid).split("-")[0]
        ev2_id = str(event2.uuid).split("-")[0]

        self.assertEqual(email.body.count(ev1_id), 1)
        self.assertEqual(email.body.count(ev2_id), 1)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=True)
    def test_email_auto_send_true(self, mock_backend):
        """
        EMAIL_AUTO_SEND=True (default): EmailMessage created + dispatched + sent.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event.save()
        case = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case.save()
        event.case = case
        event.save()

        tasks.contact_summary.delay(contact_usernames=["soporte@cert.unlp.edu.ar"])

        summary_email = EmailMessage.objects.filter(subject__contains="Summary").first()
        self.assertIsNotNone(summary_email)
        self.assertEqual(summary_email.status, "sent")
        self.assertEqual(summary_email.subject, "[TEAM][TLP:RED] Summary")
        self.assertEqual(summary_email.subject, "[TEAM][TLP:RED] Summary")
        self.assertEqual(summary_email.recipients[0]["email"], "soporte@cert.unlp.edu.ar")
        self.assertIn("Summary", summary_email.subject)
        self.assertIn("soporte@cert.unlp.edu.ar", summary_email.recipients[0]["email"])

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "[TEAM][TLP:RED] Summary")
        self.assertEqual(email.to, ["soporte@cert.unlp.edu.ar"])

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=False)
    def test_email_auto_send_false(self, mock_backend):
        """
        EMAIL_AUTO_SEND=False: EmailMessage created but NOT dispatched, no email sent.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event.save()
        case = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case.save()
        event.case = case
        event.save()

        tasks.contact_summary.delay(contact_usernames=["soporte@cert.unlp.edu.ar"])

        summary_email = EmailMessage.objects.filter(subject__contains="Summary").first()
        self.assertIsNotNone(summary_email)
        self.assertEqual(summary_email.status, "pending")
        self.assertEqual(summary_email.subject, "[TEAM][TLP:RED] Summary")

        self.assertEqual(len(mail.outbox), 0)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=True)
    def test_contact_summary_fault_tolerance(self, mock_backend):
        """
        When one contact raises an exception, the rest are still processed.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact2 = Contact.objects.create(
            name="Contact 2",
            username="contact2@test.com",
            type="email",
            role="administrative",
            priority=Priority.objects.get(slug="high"),
        )
        contact3 = Contact.objects.create(
            name="Contact 3",
            username="contact3@test.com",
            type="email",
            role="administrative",
            priority=Priority.objects.get(slug="high"),
        )

        network_a = Network.objects.create(
            cidr="10.0.0.0/8",
            active=True,
            type="internal",
            parent=self.network,
        )
        network_a.contacts.set([contact2])

        network_b = Network.objects.create(
            cidr="172.16.0.0/12",
            active=True,
            type="internal",
            parent=self.network,
        )
        network_b.contacts.set([contact3])

        event_a = Event.objects.create(
            cidr="10.0.1.1/32",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event_a.save()
        case_a = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case_a.save()
        event_a.case = case_a
        event_a.save()

        event_b = Event.objects.create(
            cidr="172.16.1.1/32",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event_b.save()
        case_b = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case_b.save()
        event_b.case = case_b
        event_b.save()

        original = Communication.communicate_contact_summary
        call_count = [0]

        def failing_communicate(contact, open_cases, closed_cases, tlp, days):
            call_count[0] += 1
            if contact.username == "contact2@test.com":
                raise RuntimeError("Simulated email failure")
            return original(contact, open_cases, closed_cases, tlp, days)

        with patch.object(
            Communication, "communicate_contact_summary", side_effect=failing_communicate
        ):
            with self.assertLogs("ngen.tasks", level="INFO") as log_capture:
                tasks.contact_summary.delay(
                    contact_usernames=["contact2@test.com", "contact3@test.com"]
                )

        self.assertGreaterEqual(call_count[0], 2)
        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary").count(), 1)
        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary", status="sent").count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["contact3@test.com"])

        logged = "\n".join(log_capture.output)
        self.assertIn("failed for contact2@test.com", logged)
        self.assertIn("done. sent=1", logged)
        self.assertIn("errors=1", logged)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=True)
    def test_contact_summary_counters(self, mock_backend):
        """
        Final log shows correct sent, skipped, errors, total counters.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact_with_case = Contact.objects.create(
            name="With Case",
            username="withcase@test.com",
            type="email",
            role="administrative",
            priority=Priority.objects.get(slug="high"),
        )
        contact_without_case = Contact.objects.create(
            name="Without Case",
            username="withoutcase@test.com",
            type="email",
            role="administrative",
            priority=Priority.objects.get(slug="high"),
        )

        network = Network.objects.create(
            cidr="192.168.0.0/16",
            active=True,
            type="internal",
            parent=self.network,
        )
        network.contacts.set([contact_with_case])

        event = Event.objects.create(
            cidr="192.168.1.1/32",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event.save()
        case = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case.save()
        event.case = case
        event.save()

        with self.assertLogs("ngen.tasks", level="INFO") as log_capture:
            tasks.contact_summary.delay(
                contact_usernames=["withcase@test.com", "withoutcase@test.com"]
            )

        logged = "\n".join(log_capture.output)
        self.assertIn("processing 2 contacts", logged)
        self.assertIn("sending to withcase@test.com open=1 closed=0", logged)
        self.assertIn("done. sent=1 skipped=1 errors=0 total=2", logged)

        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary").count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=False)
    def test_send_queued_action(self, mock_backend):
        """
        POST /api/emailmessage/{id}/send/ dispatches a stored email.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )
        from rest_framework.test import APIRequestFactory, force_authenticate
        from ngen.views.email_message import EmailMessageViewSet

        event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        event.save()
        case = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"),
        )
        case.save()
        event.case = case
        event.save()

        tasks.contact_summary.delay(contact_usernames=["soporte@cert.unlp.edu.ar"])

        summary_email = EmailMessage.objects.filter(subject__contains="Summary").first()
        self.assertIsNotNone(summary_email)
        self.assertEqual(summary_email.status, "pending")
        self.assertEqual(len(mail.outbox), 0)

        email_id = summary_email.id
        factory = APIRequestFactory()
        view = EmailMessageViewSet.as_view({"post": "send_queued"})
        request = factory.post("/api/emailmessage/{}/send/".format(email_id))
        force_authenticate(request, user=User.objects.get(username="ngen"))
        response = view(request, pk=email_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "dispatched")

        summary_email.refresh_from_db()
        self.assertEqual(summary_email.status, "sent")
        self.assertEqual(len(mail.outbox), 1)

    @override_config(EMAIL_AUTO_SEND=True)
    def test_stats_endpoint(self):
        """
        GET /api/emailmessage/stats/ returns correct counts and mode.
        """
        from rest_framework.test import APIRequestFactory, force_authenticate
        from ngen.views.email_message import EmailMessageViewSet

        EmailMessage.objects.create(
            root_message_id="m1", message_id="m1",
            senders=[{"name": "t", "email": "t@t.com"}],
            recipients=[{"name": "a", "email": "a@a.com"}],
            subject="sent", body="x",
            status="sent",
        )
        EmailMessage.objects.create(
            root_message_id="m2", message_id="m2",
            senders=[{"name": "t", "email": "t@t.com"}],
            recipients=[{"name": "b", "email": "b@b.com"}],
            subject="queued", body="x",
            status="pending",
        )
        EmailMessage.objects.create(
            root_message_id="m3", message_id="m3",
            senders=[{"name": "t", "email": "t@t.com"}],
            recipients=[{"name": "c", "email": "c@c.com"}],
            subject="failed", body="x",
            status="failed",
        )

        factory = APIRequestFactory()
        view = EmailMessageViewSet.as_view({"get": "stats"})
        request = factory.get("/api/emailmessage/stats/")
        force_authenticate(request, user=User.objects.get(username="ngen"))
        response = view(request)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertEqual(data["pending"], 1)
        self.assertEqual(data["failed"], 1)
        self.assertEqual(data["total"], 3)
        self.assertTrue(data["auto_send"])

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    def test_email_auto_send_toggle_mid_execution(self, mock_backend):
        """
        Toggling EMAIL_AUTO_SEND between calls is respected immediately.
        First call with True -> dispatched+sent. Second with False -> stored only.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact1 = Contact.objects.create(
            name="Toggle 1", username="toggle1@test.com",
            type="email", role="administrative",
            priority=Priority.objects.get(slug="high"),
        )
        contact2 = Contact.objects.create(
            name="Toggle 2", username="toggle2@test.com",
            type="email", role="administrative",
            priority=Priority.objects.get(slug="high"),
        )

        net = Network.objects.create(cidr="10.100.0.0/16", active=True, type="internal", parent=self.network)
        net.contacts.set([contact1, contact2])

        e1 = Event.objects.create(cidr="10.100.1.1/32", taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"), tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"), priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True)
        e1.save()
        c1 = Case.objects.create(state=State.objects.get(slug="open"), tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"))
        c1.save()
        e1.case = c1
        e1.save()

        # First batch: AUTO_SEND=True -> should send
        with override_config(EMAIL_AUTO_SEND=True):
            tasks.contact_summary.delay(contact_usernames=["toggle1@test.com"])

        sent_count = EmailMessage.objects.filter(subject__contains="Summary", status="sent").count()
        self.assertEqual(sent_count, 1)

        e2 = Event.objects.create(cidr="10.100.2.1/32", taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"), tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"), priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True)
        e2.save()
        c2 = Case.objects.create(state=State.objects.get(slug="open"), tlp=Tlp.objects.get(slug="green"),
            priority=Priority.objects.get(slug="high"))
        c2.save()
        e2.case = c2
        e2.save()

        # Second batch: AUTO_SEND=False -> should store only, not send
        with override_config(EMAIL_AUTO_SEND=False):
            tasks.contact_summary.delay(contact_usernames=["toggle2@test.com"])

        stored = EmailMessage.objects.filter(subject__contains="Summary", status="pending")
        self.assertEqual(stored.count(), 1)
        self.assertEqual(stored.first().recipients[0]["email"], "toggle2@test.com")

        # Total summary emails = 2, but only 1 was sent
        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary").count(), 2)
        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary", status="sent").count(), 1)
        self.assertEqual(EmailMessage.objects.filter(subject__contains="Summary", status="pending").count(), 1)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @override_config(EMAIL_AUTO_SEND=True)
    def test_contact_summary_correct_recipients(self, mock_backend):
        """
        Verify that contact_summary sends to ALL contacts with cases and to NO ONE else.
        """
        from django.utils import translation
        translation.activate("en")
        self.addCleanup(translation.deactivate)
        from django.core.mail import get_connection
        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        # Create contacts: 3 with cases, 2 without
        contacts_with = []
        contacts_without = []
        for i in range(3):
            c = Contact.objects.create(
                name=f"With Case {i}",
                username=f"withcase{i}@test.com",
                type="email",
                role="administrative",
                priority=Priority.objects.get(slug="high"),
            )
            contacts_with.append(c)
        for i in range(2):
            c = Contact.objects.create(
                name=f"Without Case {i}",
                username=f"withoutcase{i}@test.com",
                type="email",
                role="administrative",
                priority=Priority.objects.get(slug="high"),
            )
            contacts_without.append(c)

        # Each "with case" contact gets their own network with an event in an open case
        for i, contact in enumerate(contacts_with):
            net = Network.objects.create(
                cidr=f"10.{i}.0.0/16",
                active=True,
                type="internal",
                parent=self.network,
            )
            net.contacts.set([contact])
            event = Event.objects.create(
                cidr=f"10.{i}.1.1/32",
                taxonomy=Taxonomy.objects.get(slug="botnet"),
                feed=Feed.objects.get(slug="csirtamericas"),
                tlp=Tlp.objects.get(slug="green"),
                reporter=User.objects.get(username="ngen"),
                priority=Priority.objects.get(slug="high"),
                avoid_auto_merge=True,
            )
            event.save()
            case = Case.objects.create(
                state=State.objects.get(slug="open"),
                tlp=Tlp.objects.get(slug="green"),
                priority=Priority.objects.get(slug="high"),
            )
            case.save()
            event.case = case
            event.save()

        # Run summary on ALL contacts (no filter)
        all_usernames = [c.username for c in contacts_with + contacts_without]
        tasks.contact_summary.delay(contact_usernames=all_usernames)

        # Exactly 3 summary emails should be sent (one per contact with cases)
        summary_emails = EmailMessage.objects.filter(
            subject__contains="Summary", status="sent"
        )
        self.assertEqual(summary_emails.count(), 3)

        # Each sent email goes to exactly one of the "with case" contacts
        sent_to = sorted(e.recipients[0]["email"] for e in summary_emails)
        expected_to = sorted(c.username for c in contacts_with)
        self.assertEqual(sent_to, expected_to)

        # No summary email was sent to any "without case" contact
        for c in contacts_without:
            self.assertNotIn(
                c.username,
                [e.recipients[0]["email"] for e in summary_emails],
            )

        self.assertEqual(len(mail.outbox), 1 * len(contacts_with))

    # --------------- SUMMARY ORDERING TESTS -----------------

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="green")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    def test_summary_open_cases_ordered_by_priority_then_address(self, mock_backend):
        """
        Open cases in the summary should be ordered by priority (severity asc)
        first, then by domain (alphabetically) and CIDR.
        """
        from django.utils import translation

        translation.activate("en")
        self.addCleanup(translation.deactivate)

        from django.core.mail import get_connection

        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        feed = Feed.objects.get(slug="csirtamericas")
        taxonomy = Taxonomy.objects.get(slug="botnet")
        tlp = Tlp.objects.get(slug="green")
        reporter = User.objects.get(username="ngen")

        # Create network for the test domain
        net = Network.objects.create(
            domain="example.com",
            active=True,
            type="internal",
            parent=self.network,
        )
        net.contacts.set([self.contact])

        # Create 4 cases with different priorities and addresses
        # Priority severities: Critical(1), High(2), Medium(3), Low(4)
        # Domains used: host-a < host-b < host-c < host-d alphabetically

        # Case A: Medium(3), domain host-a.example.com
        case_a = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=tlp,
            priority=Priority.objects.get(slug="medium"),
        )
        ev_a = Event.objects.create(
            domain="host-a.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="medium"),
            avoid_auto_merge=True,
        )
        ev_a.case = case_a
        ev_a.save()

        # Case B: High(2), domain host-b.example.com
        case_b = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=tlp,
            priority=Priority.objects.get(slug="high"),
        )
        ev_b = Event.objects.create(
            domain="host-b.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        ev_b.case = case_b
        ev_b.save()

        # Case C: High(2), domain host-c.example.com (same priority as B, comes after B alphabetically)
        case_c = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=tlp,
            priority=Priority.objects.get(slug="high"),
        )
        ev_c = Event.objects.create(
            domain="host-c.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="high"),
            avoid_auto_merge=True,
        )
        ev_c.case = case_c
        ev_c.save()

        # Case D: Critical(1), domain host-d.example.com
        case_d = Case.objects.create(
            state=State.objects.get(slug="open"),
            tlp=tlp,
            priority=Priority.objects.get(slug="critical"),
        )
        ev_d = Event.objects.create(
            domain="host-d.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="critical"),
            avoid_auto_merge=True,
        )
        ev_d.case = case_d
        ev_d.save()

        tasks.contact_summary.delay(contact_usernames=["soporte@cert.unlp.edu.ar"])

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        id_a = str(case_a.uuid).split("-")[0]
        id_b = str(case_b.uuid).split("-")[0]
        id_c = str(case_c.uuid).split("-")[0]
        id_d = str(case_d.uuid).split("-")[0]

        body = email.body

        pos_a, pos_b = body.index(id_a), body.index(id_b)
        pos_c, pos_d = body.index(id_c), body.index(id_d)

        # Expected order by priority (severity asc): D(Critical=1), B(High=2), C(High=2), A(Medium=3)
        # Within High: B (host-b.example.com) before C (host-c.example.com)
        self.assertLess(pos_d, pos_b, "Critical should come before High")
        self.assertLess(pos_b, pos_c, "Within High, lower domain should come first")
        self.assertLess(pos_c, pos_a, "High should come before Medium")

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, LANGUAGE_CODE="en")
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(SUMMARY_TLP="green")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    def test_summary_closed_cases_ordered_by_priority_then_address(
        self, mock_backend
    ):
        """
        Closed cases in the summary should be ordered by priority (severity asc)
        first, then by domain (alphabetically) and CIDR.
        """
        from django.utils import translation

        translation.activate("en")
        self.addCleanup(translation.deactivate)

        from django.core.mail import get_connection

        mock_backend.return_value = get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        feed = Feed.objects.get(slug="csirtamericas")
        taxonomy = Taxonomy.objects.get(slug="botnet")
        tlp = Tlp.objects.get(slug="green")
        reporter = User.objects.get(username="ngen")
        closed_state = State.objects.get(slug="closed")

        # Create network for the test domain
        net = Network.objects.create(
            domain="example.com",
            active=True,
            type="internal",
            parent=self.network,
        )
        net.contacts.set([self.contact])

        # Case X: Low(4), address aaa.example.com
        case_x = Case.objects.create(
            state=closed_state,
            tlp=tlp,
            priority=Priority.objects.get(slug="low"),
        )
        ev_x = Event.objects.create(
            domain="aaa.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="low"),
            avoid_auto_merge=True,
        )
        ev_x.case = case_x
        ev_x.save()

        # Case Y: Medium(3), address zzz.example.com
        case_y = Case.objects.create(
            state=closed_state,
            tlp=tlp,
            priority=Priority.objects.get(slug="medium"),
        )
        ev_y = Event.objects.create(
            domain="zzz.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="medium"),
            avoid_auto_merge=True,
        )
        ev_y.case = case_y
        ev_y.save()

        # Case Z: Medium(3), address mmm.example.com (same priority as Y, lower address)
        case_z = Case.objects.create(
            state=closed_state,
            tlp=tlp,
            priority=Priority.objects.get(slug="medium"),
        )
        ev_z = Event.objects.create(
            domain="mmm.example.com",
            taxonomy=taxonomy,
            feed=feed,
            tlp=tlp,
            reporter=reporter,
            priority=Priority.objects.get(slug="medium"),
            avoid_auto_merge=True,
        )
        ev_z.case = case_z
        ev_z.save()

        tasks.contact_summary.delay(contact_usernames=["soporte@cert.unlp.edu.ar"])

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        id_x = str(case_x.uuid).split("-")[0]
        id_y = str(case_y.uuid).split("-")[0]
        id_z = str(case_z.uuid).split("-")[0]

        body = email.body

        # All three should appear
        self.assertIn(id_x, body)
        self.assertIn(id_y, body)
        self.assertIn(id_z, body)

        pos_x = body.index(id_x)
        pos_y = body.index(id_y)
        pos_z = body.index(id_z)

        # Expected order by priority (severity asc): Z(Medium=3 mmm), Y(Medium=3 zzz), X(Low=4)
        self.assertLess(pos_z, pos_y, "Within Medium, lower domain should come first")
        self.assertLess(pos_y, pos_x, "Medium should come before Low")
