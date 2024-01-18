from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ngen.models import Case, Priority, Tlp, State, CaseTemplate, Event, Taxonomy, Feed, User


class TestCase(APITestCase):
    '''
    This will handle Case testcases
    '''

    fixtures = ["priority.json", "tlp.json", "user.json", "state.json", "feed.json",
                "taxonomy.json", "case_template.json", "user.json"
                ]

    @classmethod
    def setUpTestData(cls):
        basename = 'case'
        cls.url_list = reverse(f'{basename}-list')
        cls.url_detail = lambda pk: reverse(f'{basename}-detail', kwargs={'pk': pk})

        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

        cls.base_url = 'http://testserver'
        cls.priority_url = cls.base_url + reverse('priority-detail', kwargs={'pk': 2})  # 'high'
        cls.tlp_url = cls.base_url + reverse('tlp-detail', kwargs={'pk': 2})  # 'amber'
        cls.state_url = cls.base_url + reverse('state-detail', kwargs={'pk': 3})  # open
        cls.case_template_url = cls.base_url + reverse('casetemplate-detail', kwargs={'pk': 1})

        cls.priority = Priority.objects.get(slug="high")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.state = State.objects.get(slug="open")
        cls.taxonomy = Taxonomy.objects.get(slug="accessible_afp_report")
        cls.user = User.objects.get(username="ngen")
        cls.case_template = CaseTemplate.objects.get(pk=1)

    def setUp(self):
        resp = self.client.post(self.url_login_jwt, data=self.json_login, format="json")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])

    def test_case_get_list(self):
        '''
        This will test successful Case GET list
        '''

        cases = [
            Case.objects.create(
                priority=self.priority,
                tlp=self.tlp,
                casetemplate_creator=self.case_template,
                state=self.state
            ),
            Case.objects.create(
                priority=self.priority,
                tlp=self.tlp,
                casetemplate_creator=self.case_template,
                state=self.state
            )
        ]

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], len(cases))

    def test_case_get_detail(self):
        '''
        This will test successful Case GET detail
        '''

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state
        )

        response = self.client.get(self.url_detail(case.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_case_post_with_valid_events(self):
        '''
        This will test successful Case POST
        '''

        _ = Event.objects.create(
            domain='test.com',
            priority=self.priority,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user
        )
        event_url = self.base_url + reverse('event-detail', kwargs={'pk': 1})

        json_data = {
            'priority': self.priority_url,
            'tlp': self.tlp_url,
            'state': self.state_url,
            'casetemplate_creator': self.case_template_url,
            'events': [event_url]
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_case_post_with_empty_events(self):
        '''
        This will test successful Case POST
        '''

        json_data = {
            'priority': self.priority_url,
            'tlp': self.tlp_url,
            'state': self.state_url,
            'casetemplate_creator': self.case_template_url,
            'events': []
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_case_post_with_invalid_events(self):
        '''
        This will test successful Case POST
        '''

        json_data = {
            'priority': self.priority_url,
            'tlp': self.tlp_url,
            'state': self.state_url,
            'casetemplate_creator': self.case_template_url,
            'events': ['http://testserver/event/123123/']
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_case_patch(self):
        '''
        This will test successful Case PATCH
        '''

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state
        )

        another_priority_url = self.base_url + reverse('priority-detail', kwargs={'pk': 1})

        json_data = {
            'priority': another_priority_url
        }

        response = self.client.patch(self.url_detail(case.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_case_put(self):
        '''
        This will test successful Case PUT
        '''

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state
        )

        another_priority_url = self.base_url + reverse('priority-detail', kwargs={'pk': 1})

        json_data = {
            'priority': another_priority_url,
            'tlp': self.tlp_url,
            'state': self.state_url,
            'casetemplate_creator': self.case_template_url
        }

        response = self.client.put(self.url_detail(case.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_case_delete(self):
        '''
        This will test successful Case DELETE
        '''

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state
        )
        case_pk = case.pk

        response = self.client.delete(self.url_detail(case_pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Case.DoesNotExist):
            Case.objects.get(pk=case_pk)
