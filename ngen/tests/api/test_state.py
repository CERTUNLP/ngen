from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import Token

from ngen.models import State


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestState(APITestCase):
    '''
    This will handle State testcases
    '''


fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy_group.json", "taxonomy.json",
            "state.json", "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]


def setUp(self):
    url_login_jwt = reverse("token-create")
    json_login = {"username": "ngen", "password": "ngen"}
    resp = self.client.post(url_login_jwt, data=json_login, format="json")
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])


def test_list_state(self):
    """
    Test that states are being listed correctly
    """
    response = self.client.get('/api/state/')
    # Assertions for a successful response (status code 200)
    self.assertEqual(response.status_code, status.HTTP_200_OK)


def test_create_state(self):
    """
    Test API state  creation
    """
    # Simulating POST data
    state_data = {

        "name": "State Test",
        "blocked": "false",
        "attended": "false",
        "solved": "false",
        "active": "false",
        "description": "",
    }

    # POST the data
    response = self.client.post('/api/state/', state_data, format='json')

    # Assertions for a successful creation (status code 201)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)


def test_update_state(self):
    """
    Test API State update
    """
    # Creating a test State
    state = State.objects.create(
        name='Test State',
        blocked=False,
        attended=False,
        solved=False,
        active=True,
        description='This is a test state'
    )
    # Update data for the state
    updated_data = State.objects.create(
        name='Updated State',
        blocked=False,
        attended=False,
        solved=False,
        active=True,
        description='This is a test state'
    )
    # POST the data
    response = self.client.put(f'/api/state/{state.id}/', updated_data, format='json')

    # Assertions for a successful update (status code 200)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Assertions to check the object is updated in the database
    state.refresh_from_db()
    self.assertEqual(stated.name, 'Updated State')


def test_delete_state(self):
    """
    Test API State deletion
    """
    # Creating a test State
    state = State.objects.create(
        name='Test State',
        blocked=False,
        attended=False,
        solved=False,
        active=True,
        description='This is a test state'
    )

    response = self.client.delete(f'/api/state/{state.id}/')

    # Assertions for a successful delete (status code 204)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Assertion to check that the database doesn't contain the deleted State
    self.assertFalse(State.objects.filter(id=state.id).exists())
