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
        self.state=State.objects.get(name="Initial") 
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



#------------------------------CASE-TESTS------------------------------------------

#---------------------------------INITIAL------------------------------------------

    def test_case_initial(self):
        """
        Creating case: INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
        priority=self.priority, #High
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=State.objects.get(name="Initial") 
        )       
        print(mail.outbox[0].subject)
        self.assertEqual(len(mail.outbox), 0) # No email for Initial. 

        


#---------------------------------STAGING------------------------------------------
    
    def test_case_staging(self):
        """
        Creating case: STAGING. Mail: NO
        """
        self.case = Case.objects.create(
        priority=self.priority, #High
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=State.objects.get(name="Staging") 
        )
        
        self.assertEqual(len(mail.outbox), 0) # No email for Staging. 

#---------------------------------OPEN---------------------------------------------

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
 
        self.assertEqual(len(mail.outbox), 1) # Test if the email is being sent. 
        self.assertEqual("New case", mail.outbox[0].subject)  # FAIL: New Case =/= New open Case

#---------------------------------CLOSED-------------------------------------------
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
        print(mail.outbox[0].subject)
        self.assertEqual(len(mail.outbox), 0) # No email for Closed. FAIL: New Case.

#---------------------------------INITIAL-INITIAL----------------------------------

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
        print(mail.outbox[0].subject)
        self.assertEqual(len(mail.outbox), 0) #  No email for Initial> Initial. FAIL: New Case.

#---------------------------------INITIAL-STAGING----------------------------------

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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) #  No email for Initial> Staging. FAIL: 2 emails: New Case + Case Status Updated.
        
#---------------------------------INITIAL-OPEN-------------------------------------

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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) #  1 Mail for Case Opened: New Case. FAIL: 2 emails: New Case + Case Opened.
        
#---------------------------------INITIAL-CLOSED-----------------------------------

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
        self.case.save()
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) #  FAIL: 2 emails: New Case + Case Closed.
        
#---------------------------------STAGING-INITIAL----------------------------------

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
        self.case.save()
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) #  FAIL: 2 emails: New Case + Case status Updated.
        
#---------------------------------STAGING-STAGING----------------------------------

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
        print(mail.outbox[0].subject)
        self.assertEqual(len(mail.outbox), 0) # FAIL:  New Case 
        
#---------------------------------STAGING-OPEN-------------------------------------

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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) # FAIL: New Case + Case opened
        
#---------------------------------STAGING-CLOSED-----------------------------------

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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) # FAIL: New Case + Case Closed
        
#---------------------------------OPEN-INITIAL-------------------------------------

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
        self.case.save()
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) # FAIL: New Open Case + Case status Updated.
        
#---------------------------------OPEN-STAGING-------------------------------------


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
        self.case.save()
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) # FAIL: New Open Case + Case status Updated. Open + Staging not permitted.
        
#---------------------------------OPEN-OPEN----------------------------------------


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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) # FAIL: 1 email: New Open Case 
        
#---------------------------------OPEN-CLOSED--------------------------------------


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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 0) # 
        
#---------------------------------CLOSED-INITIAL-----------------------------------



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
        self.case.save()
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 2) # New Open Case + Case Closed. Está bien así?
        
#---------------------------------CLOSED-STAGING-----------------------------------

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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 2) # New Open Case + Case Closed. Está bien así?
        
#---------------------------------CLOSED-OPEN--------------------------------------


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
        self.case.save()
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 2) # New Open Case + Case Closed. Está bien así?
        
#---------------------------------CLOSED-CLOSED------------------------------------

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
        print(mail.outbox[0].subject)
        print(mail.outbox[1].subject)
        self.assertEqual(len(mail.outbox), 2) # New Open Case + Case Closed. Está bien así?
        
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
        #print(mail.outbox[0].subject)
        #print(mail.outbox[1].subject)


    # def test_case_communication(self):
    #     # Call the method that triggers the communication workflow
    #     self.case_test = Case.objects.create(
    #     priority=self.priority, #High
    #     tlp=self.tlp,
    #     casetemplate_creator=self.case_template,
    #     state=State.objects.get(name="Initial") 
    #     ) 
    #     self.case_test.communicate('Test Title', 'test_template.html', event_by_contacts={})

    #     # Check if the email is in the outbox
    #     self.assertEqual(len(mail.outbox), 1)

    #     # Check recipients
    #     expected_recipients = ['test@example.com']  
    #     self.assertEqual(mail.outbox[0].to, expected_recipients)

    #     # TODO: Add more checks as needed (attachments, email content, etc.)

    #     # Simulate sending the email
    #     client = Client()
    #     response = client.get('/path/to/your/view/that/triggers/communication/')
    #     self.assertEqual(response.status_code, 200)

    #     # Check if the email was sent
    #     self.assertEqual(len(mail.outbox), 2)  # Assuming the second email was sent during the view execution


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
        #print(mail.outbox[0].body)
        #print(mail.outbox[0].attachments)
        sent_email = mail.outbox[0]
        self.assertEqual(len(sent_email.attachments), 1)

# #----------------------------------------------------------------------------------
    def test_case_init_email(self):
        """
        Creating case: INITIAL. Mail: NO
        """
        self.case = Case.objects.create(
        priority=self.priority, #High
        tlp=self.tlp,
        casetemplate_creator=self.case_template,
        state=State.objects.get(name="Initial") 
        )       
        self.assertEqual(len(mail.outbox), 0) # No email for Initial. FAIL: New Case.
        self.assertEqual(mail.outbox[0].to, "team@ngen.com")

# ----------------------------------------------------------------------------------
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
            case_state=self.state,
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
        self.event.refresh_from_db()
        last_case = Case.objects.order_by('-id').first()
        print(last_case)
        self.assertEqual(last_case, self.event.case)
        self.event.case.state = State.objects.get(name='Closed')
        self.event.case.save()
        self.assertEqual(len(mail.outbox), 1) # No manda el email. No se crea el caso?


# ----------------------------------------------------------------------------------


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
      
    #  

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
