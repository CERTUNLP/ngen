from django.test import TestCase
from django.test import Client
from django.core import mail
from ngen.models import Communication, Announcement, Tlp, Network, NetworkEntity, Priority, Taxonomy, Event, Feed, State, Case, CaseTemplate, User, Task, Playbook, config
from datetime import timedelta
from django.template.loader import get_template
from django.conf import settings

class AnnouncementTestCase(TestCase):

    fixtures = ["priority.json", "tlp.json", "user.json", "state.json",
                "feed.json", "taxonomy.json", "case_template.json"
                ]
    

    def setUp(self):
        """SetUp for case and event creation in the tests"""
        self.priority = Priority.objects.get(name="High")
        self.tlp = Tlp.objects.get(name="Green")
        self.state = State.objects.get(name="Open") 
        self.case_template = CaseTemplate.objects.get(pk=1) #Missing
        self.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        self.feed = Feed.objects.get(slug="shodan", name="Shodan")
        self.user= User.objects.create(
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

        self.case_template = CaseTemplate.objects.create(
            priority=self.priority,
            cidr=None,
            domain="info.unlp.edu.ar",
            event_taxonomy=self.taxonomy,
            event_feed=self.feed,
            case_tlp=self.tlp,
            case_state=self.state,
            case_lifecycle="auto_open",
            active=True,
        )



#------------------------------CASE-TESTS------------------------------------------

    def test_case_creation_email(self):
        """
        Creating an open case, then testing the email sending functionality
        """
        self.case = Case.objects.create(
        priority=self.priority, #High
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=self.state #Open
        )
        
        self.assertEqual(len(mail.outbox), 1) # Test if the email is being sent.

#----------------------------------------------------------------------------------
    def test_case_new_email(self):
        """
        Creating an open case, then testing "new open case" email. (Esto había que cambiarlo)
        """
        self.case = Case.objects.create(
        priority=self.priority,
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=self.state
        )
        
        self.assertEqual(len(mail.outbox), 1) # Test if the email is being sent. 
        self.assertIn("New open case", mail.outbox[0].subject)   # Change to NewCase?
#----------------------------------------------------------------------------------
    def test_case_close_email(self):
        """
        Creating an open case, then testing case closed email.
        """
        self.case = Case.objects.create(
        priority=self.priority,
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=State.objects.get(name="Open") 
        )
        # Update and close the case
        self.case.state=State.objects.get(name="Closed")        
        self.case.save()
        self.assertEqual(self.case.state.name, 'Closed')
        self.assertEqual(len(mail.outbox), 2) # Test if inbox has 2 emails, one for open and other for close.
        self.assertIn("Case closed", mail.outbox[1].subject) #Check for the title of the second email.
#----------------------------------------------------------------------------------

    def test_case_open_email(self):
        """
        Creating a case on initial, then testing "New open case" email.
        """
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=State.objects.get(name="Initial")
        )
        self.case.state = State.objects.get(name='Open')
        self.case.save()
        self.assertEqual(len(mail.outbox), 1) # Test if the email is being sent. 
        self.assertIn("Case opened", mail.outbox[0].subject)   
        self.assertIn("New case", mail.outbox[0].subject) 
        
#----------------------------------------------------------------------------------
    def test_case_update_email(self):
        """
        Creating a case, then testing case update email.
        """
        self.case = Case.objects.create(
        priority=self.priority,
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=self.state
        )
        self.case.state=State.objects.get(name='Staging') #Change to staging to force update from hook.
        self.case.before_update()
        self.assertEqual(len(mail.outbox), 3) # New open case > Case Opened > X attended X solved for update

        # self.assertIn("Case status updated", mail.outbox[2].subject)
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)



# #-------------------------------EVENT-TESTS----------------------------------------
    def test_event_creation_email_delivery(self):
        """
        Creating an event, then testing event creation email.
        """
        self.case = Case.objects.create(
        priority=self.priority, #High
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=self.state #Open
        )
        #Duda, el email es del caso
        self.event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
            case=self.case
        )
        
        self.assertEqual(len(mail.outbox), 1) # Test if the email is being sent.
        print(mail.outbox[0].body)
        print(mail.outbox[0].attachments)
        sent_email = mail.outbox[0]
        self.assertEqual(len(sent_email.attachments), 1)

# #----------------------------------------------------------------------------------



#crear case template > crear evento > revisar que se haya creado el caso ': el correo adentro deberia tener el evento
#cuadno el caso tiene un evento asociado deberia contenter al evento









        # email_contact_list = self.case.email_contacts()
        # self.assertEqual(mail.outbox[0].to, email_contact_list) # Returns empty!

        # print("Subject:")
        # print(mail.outbox[0].subject)
        # print("Body:")
        # print(mail.outbox[0].body)
        # print("From:")
        # print(mail.outbox[0].from_email)
        # print("To:")
        # print(mail.outbox[0].to)
        # print("To2:")
        # print(self.case.email_contacts())
        # print('START HERE')
        # print(mail.outbox[0].alternatives[0])
      
    #     self.example_entity = NetworkEntity.objects.create(name='Example Entity')
    #     self.example_network = Network.objects.create(cidr='163.10.0.0/16', network_entity=self.example_entity)
    #     self.tlp = Tlp.objects.create(
    #         color='#FF0000',
    #         when='Test when text',
    #         why='Test why text',
    #         information='Test info',
    #         description='Test description',
    #         encrypt=False,
    #         name='Test TLP',
    #         code=123
    #     )
    #     # Create an instance of the Announcement model
    #     announcement = Announcement.objects.create(
    #         title="Test Announcement",
    #         body="Test body content",
    #         lang='en',
    #         tlp=self.tlp,
    #         network=self.example_network
    #     )


    # def test_send_mail(self):
    #     """Testing django MAIL send property """

    #     #Creating a test mail
    #     mail.send_mail(
    #         'Example subject here',
    #         'Here is the message.',
    #         'from@example.com',
    #         ['to@example.com']
    #     )
    #     #Assert for content, deliverance, etc
    #     assert len(mail.outbox) == 1, "Inbox is not empty"
    #     assert mail.outbox[0].subject == 'Example subject here'
    #     assert mail.outbox[0].body == 'Here is the message.'
    #     assert mail.outbox[0].from_email == 'from@example.com'
    #     assert mail.outbox[0].to == ['to@example.com']

    # def test_communication_email_content(self):
    #     """
    #         Testing the send_mail method from Communication.
    #         This method receives the params:
    #         subject, content, recipients, attachments, extra_headers)
    #     """
    #     #Called from communicate = Send mail + render_template
    #     subject = "Test Subject"
    #     content = {"text": "Test text", "html": "Test HTML"}
    #     recipients =  {"from": "sender@example.com", "to": ["recipient@example.com"], "bcc": [],
    #                                         "cc": []}
    #     attachments = []
    #     extra_headers = {"X-Custom-Header": "Custom Value"}

    #     # Call the method
    #     Communication.send_mail(subject, content, recipients, attachments, extra_headers)
    #     #Check inbox is not empty
    #     assert len(mail.outbox) == 1, "Inbox is not empty"
    #     # Check the email subject and recipients
    #     sent_email = mail.outbox[0]
    #     self.assertEqual(sent_email.subject, "Test Subject")
    #     self.assertEqual(sent_email.recipients(),
    #                      ["recipient@example.com"])

    #     # Check email content
    #     self.assertIn("Test text", sent_email.body)
    #     self.assertIn("Test HTML", sent_email.alternatives[0][0])


    # @hook(AFTER_UPDATE, when="case", has_changed=True, is_not=None)
    # def case_assign_communication(self):
    #     if self.case.events.count() >= 1:
    #         self.case.communicate(gettext_lazy('New event on case'), 'reports/case_assign.html',
    #                               event_by_contacts={tuple(self.email_contacts()): [self]})

                              #No usar PK
# Probar TODOSSS los casos
