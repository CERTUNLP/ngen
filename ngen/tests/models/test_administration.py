from datetime import timedelta

from django.test import TestCase

from ngen.models import Feed, Priority, Tlp, User, config


class TestAdministration(TestCase):

    @classmethod
    def setUpTestData(cls):
        default_priority, created = Priority.objects.get_or_create(
            name=config.PRIORITY_DEFAULT,
            severity=1
        )
        cls.priority = Priority.objects.create(
            name='Test Priority',
            severity=2,
            attend_time=timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT),
            solve_time=timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT),
            notification_amount=3,
            color='#FF0000'
        )
        cls.feed = Feed.objects.create(name='Test Feed', active=True)
        cls.tlp = Tlp.objects.create(
            color='#FF0000',
            when='Test when text',
            why='Test why text',
            information='Test info',
            description='Test description',
            encrypt=False,
            name='Test TLP',
            code=123
        )
        cls.user = User.objects.create(username='testuser', password='testuser', email='test@example.com',
                                        priority=cls.priority)

        '''
        ------------------------------------------------------------------------------------------------------
        TEST CREATIONS
        '''

    def test_feed_creation(self):
        '''
        Test Feed model Creation
        '''
        self.assertEqual(str(self.feed), 'Test Feed')
        self.assertTrue(self.feed.active)

    def test_priority_model(self):
        '''
        Test Priority model Creation
        '''
        self.assertEqual(str(self.priority), 'Test Priority')
        self.assertEqual(self.priority.severity, 2)
        self.assertEqual(self.priority.attend_time, timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT))
        # AttributeError: 'Settings' object has no attribute 'PRIORITY_ATTEND_TIME_DEFAULT'
        self.assertEqual(self.priority.solve_time, timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT))
        self.assertEqual(self.priority.notification_amount, 3)
        self.assertEqual(self.priority.color, '#FF0000')

    def test_tlp_model(self):
        '''
        Test tlp model Creation
        '''
        self.assertEqual(str(self.tlp), 'Test TLP')
        self.assertEqual(self.tlp.code, 123)
        self.assertEqual(self.tlp.color, '#FF0000')
        self.assertEqual(self.tlp.when, 'Test when text')
        self.assertEqual(self.tlp.why, 'Test why text')
        self.assertEqual(self.tlp.information, 'Test info')
        self.assertEqual(self.tlp.description, 'Test description')
        self.assertFalse(self.tlp.encrypt)

    def test_user_model(self):
        '''
        Test user model Creation
        '''
        self.assertEqual(str(self.user), 'testuser')
        self.assertIsNone(self.user.api_key)

        '''
        END TEST CREATIONS
        ------------------------------------------------------------------------------------------------------
        '''

    def test_user_priority(self):
        '''
        Test user priority
        '''
        self.assertEqual(self.user.priority.name, 'Test Priority')
        self.assertEqual(self.user.priority.severity, 2)
