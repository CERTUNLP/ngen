from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import Token


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestConstance(APITestCase):
    '''
    This will handle constance testcases
    '''

    fixtures = ["priority.json", "user.json"]

    # fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json",
    # "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]

    @classmethod
    def setUpTestData(cls):
        basename = 'constance'
        cls.url_list = reverse(f'{basename}-list')
        cls.url_detail = lambda key: reverse(
            f'{basename}-detail', kwargs={'key': key})
        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

    def setUp(self):
        resp = self.client.post(
            self.url_login_jwt, data=self.json_login, format="json")
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])

    def test_constance_get(self):
        '''
        This will test successfull constance get
        '''
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_constance_get_team_abuse(self):
        '''
        This will test successfull constance get team email
        '''
        response = self.client.get(self.url_detail(key='TEAM_ABUSE'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data['key'], "TEAM_ABUSE")
        self.assertEqual(response.data['value'], "abuse@ngen.com")
        self.assertEqual(response.data['value_type'], "str")
        self.assertEqual(response.data['help_text'], "CSIRT abuse email")
        self.assertEqual(response.data['default'], "abuse@ngen.com")

    def test_constance_post(self):
        '''
        This will test error constance post
        '''
        response = self.client.post(
            self.url_detail(key='TEAM_EMAIL'), {'value': 'test'})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_put(self):
        '''
        This will test sucessfull constance put with get param
        '''
        new_value = "test_new_put@test.com"
        response = self.client.put(self.url_detail(
            key='TEAM_EMAIL'), {"value": new_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url_detail(key='TEAM_EMAIL'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], new_value)

    def test_constance_patch(self):
        '''
        This will test sucessfull constance patch with get param
        '''
        new_value = "test_new_patch@test.com"
        # url = reverse(self.url_detail(key='TEAM_EMAIL'))
        response = self.client.patch(self.url_detail(
            key='TEAM_EMAIL'), {"value": new_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url_detail(key='TEAM_EMAIL'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], new_value)

    def test_constance_delete(self):
        '''
        This will test error constance delete
        '''
        response = self.client.delete(self.url_detail(key='TEAM_EMAIL'))
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_get_invalid_key(self):
        '''
        This will test error constance get invalid key with get param
        '''
        response = self.client.get(self.url_detail(key='TEAM_EMAIL_INVALID'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_post(self):
        '''
        This will test error constance get invalid key with post and get param
        '''
        response = self.client.post(self.url_detail(
            key='TEAM_EMAIL_INVALID'), {'value': 'test'})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_get_invalid_key_put(self):
        '''
        This will test error constance get invalid key with put and get param
        '''
        response = self.client.put(self.url_detail(
            key='TEAM_EMAIL_INVALID'), {'value': 'test'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_patch(self):
        '''
        This will test error constance get invalid key with patch and get param
        '''
        response = self.client.patch(self.url_detail(
            key='TEAM_EMAIL_INVALID'), {'value': 'test'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_delete(self):
        '''
        This will test error constance get invalid key with delete and get param
        '''
        response = self.client.delete(
            self.url_detail(key='TEAM_EMAIL_INVALID'))
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
