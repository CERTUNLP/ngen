from datetime import timedelta

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from rest_framework_simplejwt.tokens import (
    Token,
)

class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestConstance(APITestCase):
    '''
    This will handle constance testcases
    '''

    fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json", "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]

    def setUp(self):
        basename = 'constance'
        self.basename_detail = f'{basename}-detail'
        self.basename_list = f'{basename}-list'
        self.url = reverse(self.basename_list)
        url_login_jwt = reverse("token-create")
        json_login = {"username": "ngen", "password": "ngen"}
        resp = self.client.post(url_login_jwt, data=json_login, format="json")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])
    
    def test_constance_get(self):
        '''
        This will test successfull constance get
        '''
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_constance_get_team_email(self):
        '''
        This will test successfull constance get team email
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data['key'], "TEAM_EMAIL")
        self.assertEqual(response.data['value'], "team@ngen.com")
        self.assertEqual(response.data['value_type'], "str")
        self.assertEqual(response.data['help_text'], "CSIRT team email")
        self.assertEqual(response.data['default'], "team@ngen.com")

    def test_constance_post(self):
        '''
        This will test error constance post
        '''
        response = self.client.post(self.url, {"key": "TEAM_EMAIL", "value": "test"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_put(self):
        '''
        This will test sucessfull constance put with get param
        '''
        new_value = "test_new_put@test.com"
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL'})
        response = self.client.put(url, {"value": new_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], new_value)
    
    def test_constance_patch(self):
        '''
        This will test sucessfull constance patch with get param
        '''
        new_value = "test_new_patch@test.com"
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL'})
        response = self.client.patch(url, {"value": new_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], new_value)
    
    def test_constance_delete(self):
        '''
        This will test error constance delete
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_get_invalid_key(self):
        '''
        This will test error constance get invalid key with get param
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL_INVALID'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_post(self):
        '''
        This will test error constance get invalid key with post and get param
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL_INVALID'})
        response = self.client.post(url, {'value': 'test'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_get_invalid_key_put(self):
        '''
        This will test error constance get invalid key with put and get param
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL_INVALID'})
        response = self.client.put(url, {'value': 'test'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_patch(self):
        '''
        This will test error constance get invalid key with patch and get param
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL_INVALID'})
        response = self.client.patch(url, {'value': 'test'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_delete(self):
        '''
        This will test error constance get invalid key with delete and get param
        '''
        url = reverse(self.basename_detail, kwargs={'key': 'TEAM_EMAIL_INVALID'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
