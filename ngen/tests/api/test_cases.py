from datetime import timedelta
from django.urls import reverse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import Token

class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)

class TestCase(APITestCase):
    '''
    This will handle Case testcases
    '''

    fixtures = ["priority.json", "tlp.json", "user.json", "state.json",
                "feed.json", "taxonomy.json", "case_template.json"
    ]

    @classmethod
    def setUpTestData(cls):
        basename = 'case'
        cls.url = reverse(f'{basename}-list')
        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

        cls.base_url = 'http://testserver'
        cls.priority_url = cls.base_url + reverse('priority-detail', kwargs={'pk': 2}) # 'high'
        cls.tlp_url = cls.base_url + reverse('tlp-detail', kwargs={'pk': 2}) # 'amber'
        cls.state = cls.base_url + reverse('state-detail', kwargs={'pk': 9}) # open
        cls.case_template = cls.base_url + reverse('casetemplate-detail', kwargs={'pk': 1})

    def setUp(self):
        resp = self.client.post(self.url_login_jwt, data=self.json_login, format="json")
        print(resp.data)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])

    def test_case_post(self):
        '''
        This will test successfull Case POST
        '''
        json_data = {
            'priority': self.priority_url,
            'tlp': self.tlp_url,
            'state': self.state,
            'casetemplate_creator': self.case_template
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
