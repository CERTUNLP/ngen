from django.urls import reverse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ngen.models import Case, Priority, Tlp, State, CaseTemplate

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
        cls.url_list = reverse(f'{basename}-list')
        cls.url_detail = lambda pk: reverse(f'{basename}-detail', kwargs={'pk': pk})

        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

        cls.base_url = 'http://testserver'
        cls.priority_url = cls.base_url + reverse('priority-detail', kwargs={'pk': 2}) # 'high'
        cls.tlp_url = cls.base_url + reverse('tlp-detail', kwargs={'pk': 2}) # 'amber'
        cls.state_url = cls.base_url + reverse('state-detail', kwargs={'pk': 9}) # open
        cls.case_template_url = cls.base_url + reverse('casetemplate-detail', kwargs={'pk': 1})

        cls.priority = Priority.objects.get(pk=2)
        cls.tlp = Tlp.objects.get(pk=2)
        cls.state = State.objects.get(pk=9)
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

    def test_case_post(self):
        '''
        This will test successful Case POST
        '''

        json_data = {
            'priority': self.priority_url,
            'tlp': self.tlp_url,
            'state': self.state_url,
            'casetemplate_creator': self.case_template_url
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
