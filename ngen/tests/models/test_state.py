from django.test import TestCase
from ngen.models import State, Edge, NgenModel, Case  

class StateTestCase(TestCase):

    def setUp(self):
        # Create multiple States for testing
        self.first_state = State.objects.create(name='First State', active=True)
        self.second_state = State.objects.create(name='Second State', active=True)        
    def test_state_creation(self):
        state = State.objects.create(
            name='Test State',
            blocked=False,
            attended=False,
            solved=False,
            active=True,
            description='This is a test state'
        )
        self.assertEqual(state.__str__(), 'Test State')
        self.assertEqual(state.slug, 'test_state')


    def test_edge_creation(self):
        edge = Edge.objects.create(parent=self.first_state, child=self.second_state, discr='Test Edge')
        self.assertEqual(edge.__str__(), 'First State -> Second State')

    def test_edge_deletion(self):
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


    def test_state_deletion(self):
        # Create a state
        state_to_delete = State.objects.create(name='State to Delete', active=True)

        # Create another state
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
#./manage.py test ngen.tests.models.test_state
"""