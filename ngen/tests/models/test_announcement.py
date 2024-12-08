from constance.test import override_config
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.utils.translation import gettext_lazy

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
            type="external",
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
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

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
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

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
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

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
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

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
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

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
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

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
        self.case.state = State.objects.get(name="Closed")
        self.case.save()

        intern_channel = self.case.communication_channels.filter(
            communication_types__type="intern"
        ).first()

        self.assertIsNotNone(intern_channel)
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
            intern_channel.get_last_message().subject,
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
            priority=self.priority,
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
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

        # Assert email was sent in affected channel
        self.assertIsNotNone(affected_channel)
        self.assertEqual(len(affected_channel.get_messages()), 1)
        self.assertIn(
            str(gettext_lazy("Case opened")),
            affected_channel.get_last_message().subject,
        )

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
            priority=self.priority,
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
        self.assertEqual(len(intern_channel.get_messages()), 1)
        self.assertIn(
            str(gettext_lazy("Case opened")), intern_channel.get_last_message().subject
        )

        # Assert email was sent in affected channel
        self.assertIsNotNone(affected_channel)
        self.assertEqual(len(affected_channel.get_messages()), 1)
        self.assertIn(
            str(gettext_lazy("Case opened")),
            affected_channel.get_last_message().subject,
        )

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
            priority=self.priority,
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
            priority=self.priority,
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
            priority=self.priority,
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
