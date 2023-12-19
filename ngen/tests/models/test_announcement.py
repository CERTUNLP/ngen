from django.core import mail
from ngen.models import Evidence, ContentType, Tlp, Priority, \
    Taxonomy, Event, Feed, State, Case, CaseTemplate, User, Task, Playbook

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase


class AnnouncementTestCase(TestCase):
    fixtures = ["priority.json", "tlp.json", "user.json", "state.json", "edge.json",
                "feed.json", "taxonomy.json", "case_template.json"
                ]

    def setUp(self):
        """SetUp for case and event creation in the tests"""
        self.priority = Priority.objects.get(name="High")
        self.tlp = Tlp.objects.get(name="Green")
        self.state = State.objects.get(name="Open")
        self.case_template = CaseTemplate.objects.get(pk=1)  # Missing
        self.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        self.feed = Feed.objects.get(slug="shodan", name="Shodan")
        self.user = User.objects.create(
            username="test",
            password="test",
            priority=self.priority
        )
        self.playbook = Playbook.objects.create(
            name="Test playbook",
        )
        self.task = Task.objects.create(
            name="Test task",
            description="Test description",
            playbook=self.playbook,
            priority=self.priority,
        )

        # self.case_template = CaseTemplate.objects.create(
        #     priority=self.priority,
        #     cidr=None,
        #     domain="info.unlp.edu.ar",
        #     event_taxonomy=self.taxonomy,
        #     event_feed=self.feed,
        #     case_tlp=self.tlp,
        #     case_state=self.state,
        #     case_lifecycle="auto_open",
        #     active=True,
        # )

    # ------------------------------CASE-TESTS------------------------------------------

    # ---------------------------------INITIAL------------------------------------------

    def test_case_initial(self):
        """
        Creating case: INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,  # High
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial")
        )
        self.assertEqual(len(mail.outbox), 0)  # No email for Initial.

    # ---------------------------------STAGING------------------------------------------

    def test_case_staging(self):
        """
        Creating case: STAGING. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,  # High
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging")
        )

        self.assertEqual(len(mail.outbox), 0)  # No email for Staging.

    # ---------------------------------OPEN---------------------------------------------

    def test_case_open(self):
        """
        Creating case: OPEN. Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open")
        )

        self.assertEqual(len(mail.outbox), 1)  # Test if the email is being sent.
        self.assertIn("Case opened", mail.outbox[0].subject)

    # ---------------------------------CLOSED-------------------------------------------
    def test_case_closed(self):
        """
        Creating case: CLOSED. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed")
        )
        self.assertEqual(len(mail.outbox), 0)  # No email for Closed.

    # ---------------------------------INITIAL-INITIAL----------------------------------

    def test_case_initial_initial(self):
        """
        Creating a case: INITIAL > INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial")
        )
        self.case.state = State.objects.get(name='Initial')
        self.case.save()
        self.assertEqual(len(mail.outbox), 0)  # No email for Initial> Initial. FAIL: New Case.

    # ---------------------------------INITIAL-STAGING----------------------------------

    def test_case_initial_staging(self):
        """
        Creating a case: INITIAL > STAGING. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial")
        )
        self.case.state = State.objects.get(name='Staging')
        self.case.save()
        self.assertEqual(len(mail.outbox), 0)

    # ---------------------------------INITIAL-OPEN-------------------------------------

    def test_case_initial_open(self):
        """
        Creating a case: INITIAL > OPEN. Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial")
        )
        self.case.state = State.objects.get(name='Open')
        self.case.save()
        self.assertEqual(len(mail.outbox), 1)  # Case Opened.

    # ---------------------------------INITIAL-CLOSED-----------------------------------

    def test_case_initial_closed(self):
        """
        Creating a case: INITIAL > CLOSED. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial")
        )
        self.case.state = State.objects.get(name='Closed')
        self.case.state.save()
        self.assertEqual(len(mail.outbox), 0)

    # ---------------------------------STAGING-INITIAL----------------------------------

    def test_case_staging_initial(self):
        """
        Creating a case: STAGING > INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging")
        )
        self.case.state = State.objects.get(name='Initial')
        self.case.state.save()
        self.assertEqual(len(mail.outbox), 0)  # FAIL: 2 emails: New Case + Case status Updated.

    # ---------------------------------STAGING-STAGING----------------------------------

    def test_case_staging_staging(self):
        """
        Creating a case: STAGING > STAGING. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging")
        )
        self.case.state = State.objects.get(name='Staging')
        self.case.save()
        self.assertEqual(len(mail.outbox), 0)  # FAIL:  New Case

    # ---------------------------------STAGING-OPEN-------------------------------------

    def test_case_staging_open(self):
        """
        Creating a case: STAGING > OPEN. Mail: YES
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging")
        )
        self.case.state = State.objects.get(name='Open')
        self.case.save()
        self.assertEqual(len(mail.outbox), 1)  # FAIL: New Case + Case opened

    # ---------------------------------STAGING-CLOSED-----------------------------------

    def test_case_staging_closed(self):
        """
        Creating a case: STAGING > CLOSED. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Staging")
        )
        self.case.state = State.objects.get(name='Closed')
        self.case.save()
        self.assertEqual(len(mail.outbox), 0)  # FAIL: New Case + Case Closed

    # ---------------------------------OPEN-INITIAL-------------------------------------

    def test_case_open_initial(self):
        """
        Creating a case: open > initial. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open")
        )
        self.case.state = State.objects.get(name='Initial')
        self.case.state.save()
        self.assertEqual(len(mail.outbox), 1)  # Just the mail from Open case.

    # ---------------------------------OPEN-STAGING-------------------------------------

    def test_case_open_staging(self):
        """
        Creating a case: open > staging. Not possible
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open")
        )
        self.case.state = State.objects.get(name='Staging')
        self.case.state.save()
        self.assertEqual(len(mail.outbox), 1)  # Just the mail from Open case.

    # ---------------------------------OPEN-OPEN----------------------------------------

    def test_case_open_open(self):
        """
        Creating a case: open > open. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open")
        )
        self.case.state = State.objects.get(name='Open')
        self.case.save()
        self.assertEqual(len(mail.outbox), 1)  # 1 email will be the creation open email.

    # ---------------------------------OPEN-CLOSED--------------------------------------

    def test_case_open_closed(self):
        """
        Creating a case: open > closed. Mail: Case closed
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Open")
        )
        self.case.state = State.objects.get(name='Closed')
        self.case.save()
        self.assertIn("Case closed", mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 2)  #

    # ---------------------------------CLOSED-INITIAL-----------------------------------

    def test_case_closed_initial(self):
        """
        Creating a case: closed > Initial. Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed")
        )
        self.case.state = State.objects.get(name='Initial')
        self.case.state.save()
        self.assertEqual(len(mail.outbox), 0)

    # ---------------------------------CLOSED-STAGING-----------------------------------

    def test_case_closed_staging(self):
        """
        Creating a case: closed > Staging . Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed")
        )
        self.case.state = State.objects.get(name='Staging')
        self.case.save()
        self.assertEqual(len(mail.outbox), 1)  # Case status updated

    # ---------------------------------CLOSED-OPEN--------------------------------------

    def test_case_closed_open(self):
        """
        Creating a case: closed > . Not possible.
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed")
        )
        self.case.state = State.objects.get(name='Open')
        self.case.state.save()
        self.assertEqual(len(mail.outbox), 0)  # New Open Case + Case Closed. Está bien así?

    # ---------------------------------CLOSED-CLOSED------------------------------------

    def test_case_closed_closed(self):
        """
        Creating a case: closed > . Mail: NO
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Closed")
        )
        self.case.state = State.objects.get(name='Closed')
        self.case.save()
        self.assertEqual(len(mail.outbox), 0)  # New Open Case + Case Closed. Está bien así?

    # ----------------------------------------------------------------------------------


    # #-------------------------------EVENT-TESTS----------------------------------------
    def test_case_template_email(self):
        """
        Creating case template and coinciding event. Testing correct case integration and email sending.
        """
        self.case_template = CaseTemplate.objects.create(
            priority=self.priority,
            cidr=None,
            domain="info.unlp.edu.ar",
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=State.objects.get(name="Open"),
            case_lifecycle="auto_open",
            active=True,
        )
        self.case_template.refresh_from_db()
        self.event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )
        attachments = [
            {'name': 'attachment1.txt', 'file': b'This is the content of attachment 1.'},
            {'name': 'attachment2.txt', 'file': b'This is the content of attachment 2.'},
        ]
        self.evidence_file = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")
        self.evidence = Evidence.objects.create(
            file=self.evidence_file,
            object_id=self.event.id,
            content_type=ContentType.objects.get_for_model(Event),
        )
        self.event.refresh_from_db()
        last_case = Case.objects.order_by('-id').first()
        print(last_case)
        self.assertEqual(last_case, self.event.case)
        self.assertEqual(len(mail.outbox), 1)  # No manda el email. No se crea el caso?
        self.assertEqual(self.evidence.attachment_name,
                         f'Event({self.event.id}):{self.event.created.date()}:{self.evidence.filename}')

# ----------------------------------------------------------------------------------
# def test_send_mail_with_attachments(self):
#     # Assert the number of sent emails
#     self.assertEqual(len(mail.outbox), 1)
#     # Get the sent email
#     sent_email = mail.outbox[0]
#     # Assert attachments
#     for attachment in attachments:
#         self.assertIn(attachment['name'], sent_email.attachments)
#         self.assertEqual(sent_email.attachments[attachment['name']], attachment['file'])
