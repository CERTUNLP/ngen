from datetime import datetime, timedelta

from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.hashers import make_password
from ngen.models import User, Event, Case, CaseTemplate

from ngen.tests.api.test_authentication import BaseAPITestCase

from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
    SlidingToken,
    Token,
    UntypedToken,
)

class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestEvent(APITestCase):
    '''
    This will handle event testcases
    '''

    fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json", "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]

    def setUp(self):
        basename = 'event'
        self.url = reverse(f'{basename}-list')
        url_login_jwt = reverse("token-create")
        json_login = {"username": "ngen", "password": "ngen"}
        resp = self.client.post(url_login_jwt, data=json_login, format="json")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])
    
    def test_event_post_with_cidr(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            'cidr': '2.2.2.2',
            # 'domain': 'bbb',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/feed/1/',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_domain(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            # 'cidr': '2.2.2.2',
            'domain': 'info.unlp.edu.ar',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/feed/1/',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_slugs(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            # 'cidr': '2.2.2.2',
            'domain': 'info.unlp.edu.ar',
            'notes': 'estas son notas',
            'priority': 'critical',
            'tlp': 'amber',
            'taxonomy': 'phishing',
            'feed': 'shodan',
        }

        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_cidr_and_domain(self):
        '''
        This will test bad request event post
        '''
        json_data = {
            'cidr': '2.2.2.2',
            'domain': 'info.unlp.edu.ar',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'shodan',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_null_and_domain_null(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            # 'cidr': '',
            # 'domain': 'info.unlp.edu.ar',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'shodan',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_empty_and_domain_null(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            'cidr': '',
            # 'domain': 'info.unlp.edu.ar',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'shodan',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_null_and_domain_empty(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            # 'cidr': '',
            'domain': '',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'shodan',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_cidr_empty_and_domain_empty(self):
        '''
        This will test successfull event post
        '''
        json_data = {
            'cidr': '',
            'domain': '',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'shodan',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_cidr_wildcard_and_domain_empty(self):
        '''
        This will test bad request event post
        '''
        json_data = {
            'cidr': '0.0.0.0/0',
            'domain': '',
            'notes': 'estas son notas',
            'priority': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/priority/2/', # '2',
            'tlp': 'http://backngen.servicios.cert.unlp.edu.ar/api/administration/tlp/2/', #'amber',
            'taxonomy': 'http://backngen.servicios.cert.unlp.edu.ar/api/taxonomy/41/', #'phishing',
            'feed': 'shodan',
        }
        response = self.client.post(self.url, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_fields_not_editable(self):
        '''
        This will test successfull event post
        '''
        pass # TODO

    def test_event_post_that_matches_with_case_template(self):
        '''
        This will test a successful Event POST that matches with a Case Template,
        therefore creating a Case
        '''

        initial_case_count = Case.objects.count()

        case_template = CaseTemplate.objects.create(
            priority_id=2,
            cidr=None,
            domain='*',
            event_taxonomy_id=90,
            event_feed_id=11,
            case_tlp_id=4,
            case_state_id=9,
            case_lifecycle='auto_open',
            active=True
        )

        json_data = {
            'domain': 'info.unlp.edu.ar',
            'notes': 'Some notes',
            'priority': 'critical',
            'tlp': 'amber',
            'taxonomy': 'phishing',
            'feed': 'shodan',
        }

        response = self.client.post(self.url, data=json_data)
        new_case_count = Case.objects.count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['case'],
            f'http://testserver/api/case/{Case.objects.last().id}/'
        )
        self.assertEqual(new_case_count, initial_case_count + 1)
        self.assertEqual(Event.objects.last().case, Case.objects.last())
        self.assertEqual(Case.objects.last().casetemplate_creator, case_template)
