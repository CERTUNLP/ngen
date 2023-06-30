from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.hashers import make_password
from ngen.models import User


class TestLogin(APITestCase):
    '''
    This will handle login testcases
    '''

    fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json", "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]

    def setUp(self):
        self.user_data = {
            "first_name" : "John",
            "last_name" : "Doe",
            'email' : "email@gmail.com",
            'username' : "johnuser",
            'password' : "password"
            }
        self.url = reverse('token-create')
        User.objects.create_user(**self.user_data)
    

    def test_login(self):
        '''
        This will test successfull login
        '''
        post_data = {
            'username' : self.user_data.get('username'),
            'password' : self.user_data.get('password')
            }

        
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_login_with_wrong_password(self):
        '''
        This will test login with wrong password
        '''
        post_data = {
            'username' : self.user_data.get('username'),
            'password' : 'wrongpassword'
            }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_wrong_username(self):
        '''
        This will test login with wrong username
        '''
        post_data = {
            'username' : 'wrongusername',
            'password' : self.user_data.get('password')
            }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_login_with_empty_password(self):
        '''
        This will test login with empty password
        '''
        post_data = {
            'username' : self.user_data.get('username'),
            'password' : ''
            }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_username(self):
        '''
        This will test login with empty username
        '''
        post_data = {
            'username' : '',
            'password' : self.user_data.get('password')
            }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_username_and_password(self):
        '''
        This will test login with empty username and password
        '''
        post_data = {
            'username' : '',
            'password' : ''
            }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_username_and_password(self):
        '''
        This will test login with invalid username and password
        '''
        post_data = {
            'username' : 'invalidusername',
            'password' : 'invalidpassword'
            }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    # Not implemented yet
    # def test_login_with_email(self):
    #     '''
    #     This will test login with email
    #     '''
    #     post_data = {
    #         'username' : self.user_data.get('email'),
    #         'password' : self.user_data.get('password')
    #         }

    #     response = self.client.post(self.url, data=post_data)
    #     self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
