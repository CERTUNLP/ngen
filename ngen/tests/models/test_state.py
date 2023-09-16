from django.test import TestCase
from django.db.models import deletion
from ngen.models import State, Edge, Taxonomy, NgenModel, Case, Tlp, User, CaseTemplate, Priority, NgenPriorityMixin, config

class StateTestCase(TestCase):

    def setUp(self):
        '''
        State setup.
        '''
        # Create the default Priority instance
        default_priority, created = Priority.objects.get_or_create(
            name=config.PRIORITY_DEFAULT,
             severity=1
            )
        default_priority.save()
        self.tlp = Tlp.objects.create(name='Test TLP', code='123')
        self.user_creator = User.objects.create(username='creator')
        self.assigned_user = User.objects.create(username='assigned')
        self.state = State.objects.create(name='State')
        self.first_state = State.objects.create(name='First State', active=True)
        self.second_state = State.objects.create(name='Second State', active=True)  
        self.case_template = None

    def test_state_creation(self):
        '''
        Test State creation
        '''
        self.assertEqual(self.state.__str__(), 'State')
        self.assertEqual(self.state.slug, 'state')

    def test_state_update(self):
        '''
        Test State update
        '''
        # Updating State object
        self.state.name = 'Updated State'
        self.state.description = 'This is an updated state'
        self.state.save()

        # Retrieve the updated state from the database
        updated_state = State.objects.get(pk=self.state.pk)

        # Assertions to check if the state was updated correctly
        self.assertEqual(updated_state.name, 'Updated State')
        self.assertEqual(updated_state.description, 'This is an updated state')

    def test_state_deletion(self): 
        '''
        Test State deletion. This also tests that if you delete a State that is present in an Edge, the edge also gets deleted.
        '''
        state_to_delete = State.objects.create(name='State to Delete', active=True)
        another_state = State.objects.create(name='Another State', active=True)

        # Create an edge between the two states
        edge = Edge.objects.create(parent=state_to_delete, child=another_state, discr='Test Edge')

        # Check that the edge exists
        self.assertTrue(Edge.objects.filter(parent=state_to_delete, child=another_state).exists())

        # Delete the state
        state_to_delete.delete()

        #Check that the state is deleted
        self.assertFalse(State.objects.filter(name='State to Delete').exists())

        # Check that the edge is also deleted
        self.assertFalse(Edge.objects.filter(parent=state_to_delete, child=another_state).exists())


    def test_state_permanency(self):
        case = Case.objects.create(
        tlp=self.tlp,  
        casetemplate_creator=self.case_template,  
        user_creator=self.user_creator,  
        assigned=self.assigned_user,  
        state=self.state,  
        attend_date=None, 
        solve_date=None, 
        report_message_id=None,  
        raw=None,  
        uuid='13075770-ad80-4d1e-8df7-f88c58365b92',  
        lifecycle='manual',  
        notification_count=1,
        )
        # Try to delete test_state
        with self.assertRaises(deletion.ProtectedError):
            self.state.delete()

    def test_edge_creation(self):
        '''
        Test Edge creation
        '''
        edge = Edge.objects.create(parent=self.first_state, child=self.second_state, discr='Test Edge')
        self.assertEqual(edge.__str__(), 'First State -> Second State')

    def test_edge_update(self):
        '''
        Test Edge update
        '''    
    # Create an Edge object
        edge = Edge.objects.create(parent=self.first_state, child=self.second_state, discr='Test Edge')

    # Update the Edge object
        edge.discr = 'Updated Edge'
        edge.save()

    # Retrieve the updated edge from the database
        updated_edge = Edge.objects.get(pk=edge.pk)

    # Assertions to check if the edge was updated correctly
        self.assertEqual(updated_edge.discr, 'Updated Edge')                

    def test_edge_deletion(self):
        '''
        Test Edge deletion
        '''
        # Create an edge
        edge = Edge.objects.create(parent=self.first_state, child=self.second_state, discr='Test Edge')

        # Check if the edge was created correctly
        self.assertEqual(edge.__str__(), 'First State -> Second State')

        # Check if the states are initially connected
        self.assertTrue(self.first_state.is_parent_of(self.second_state))

        # Delete the edge
        edge.delete()

        # Check if the edge was deleted
        self.assertFalse(Edge.objects.filter(parent=self.first_state, child=self.second_state).exists())

        # Check if the states are no longer connected
        self.assertFalse(self.first_state.is_parent_of(self.second_state))




"""
        # Create a test Case for state testing
        case = Case.objects.create(
        tlp=tlp_instance,  # Replace with the actual Tlp object
        date=datetime.now(),  # Set the date as needed
        casetemplate_creator=None,  # Set this field if necessary
        user_creator=creator_user,  # Set the creator user
        assigned=assigned_user,  # Set the assigned user
        state=state,  # Set the state
        attend_date=None,  # Set attend_date if needed
        solve_date=None,  # Set solve_date if needed
        report_message_id=None,  # Set report_message_id if needed
        raw=None,  # Set raw data if needed
        uuid=None,  # Set the UUID if needed
        lifecycle='manual',  # Set the lifecycle as needed
        notification_count=1,  # Set notification_count as needed
        
)
#
sudo docker exec -it docker-ngen-django-1 sh
./manage.py test ngen.tests.models.test_state
./manage.py test ngen.tests.api.test_state
"""