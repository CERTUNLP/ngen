from datetime import timedelta

from rest_framework import status
from rest_framework_simplejwt.tokens import Token

from ngen.models import Priority, Tlp, Feed, config
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestAdministration(APITestCaseWithLogin):
    """
    This will handle Administration testcases
    """

    fixtures = [
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/feed.json",
    ]

    # --------------------------------------------------------TLP----------------------------------------------------------

    def test_list_tlp(self):
        """
        Test TLP listing
        """
        response = self.client.get("/api/administration/tlp/")
        # Assertions for a successful response (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_tlp(self):
        """
        Test API TLP creation
        """
        # Simulating POST data
        TLP_data = {
            "color": "#FF0000",
            "when": "false",
            "why": "false",
            "information": "false",
            "description": "false",
            "encrypt": False,
            "name": "Test TLP",
            "code": 122,
        }

        # POST the data
        response = self.client.post("/api/administration/tlp/", TLP_data, format="json")

        # Assertions for a successful creation (status code 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_tlp(self):
        """
        Test API TLP update
        """
        # Creating a test TLP
        tlp = Tlp.objects.create(
            color="#FF0000",
            when="false",
            why="false",
            information="false",
            description="This is a test TLP",
            encrypt=False,
            name="Test TLP",
            code=122,
        )

        # Updated data for the TLP
        updated_data = {
            "color": "#00FF00",
            "when": "true",
            "why": "true",
            "information": "true",
            "description": "Updated TLP description",
            "encrypt": True,
            "name": "Updated TLP",
            "code": 123,
        }

        # PUT the data
        response = self.client.put(
            f"/api/administration/tlp/{tlp.id}/", updated_data, format="json"
        )

        # Assertions for a successful update (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assertions to check the object is updated in the database
        tlp.refresh_from_db()
        self.assertEqual(tlp.name, "Updated TLP")

    def test_delete_tlp(self):
        """
        Test API TLP deletion
        """
        # Creating a test TLP
        tlp = Tlp.objects.create(
            color="#FF0000",
            when="false",
            why="false",
            information="false",
            description="This is a test TLP",
            encrypt=False,
            name="Test TLP",
            code=122,
        )

        # DELETE the TLP
        response = self.client.delete(f"/api/administration/tlp/{tlp.id}/")

        # Assertions for a successful deletion (status code 204)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assertions to check the object is deleted from the database
        with self.assertRaises(Tlp.DoesNotExist):
            tlp.refresh_from_db()

    # ----------------------------------------------------END-TLP----------------------------------------------------------

    # ------------------------------------------------------FEED-----------------------------------------------------------
    def test_create_feed(self):
        """
        Test API Feed creation
        """
        # Simulating POST data
        feed_data = {
            "name": "Test Feed",
            "active": True,
            "description": "This is a test feed",
        }

        # POST the data
        response = self.client.post(
            "/api/administration/feed/", feed_data, format="json"
        )

        # Assertions for a successful creation (status code 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_feed(self):
        """
        Test API Feed update
        """
        # Creating a test Feed
        feed = Feed.objects.create(
            name="Test Feed",
            active=True,
            description="This is a test feed",
        )

        # Updated data for the Feed
        updated_data = {
            "name": "Updated Feed",
            "active": False,
            "description": "Updated feed description",
        }

        # PUT the data
        response = self.client.put(
            f"/api/administration/feed/{feed.id}/", updated_data, format="json"
        )

        # Assertions for a successful update (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assertions to check the object is updated in the database
        feed.refresh_from_db()
        self.assertEqual(feed.name, "Updated Feed")

    def test_delete_feed(self):
        """
        Test API Feed deletion
        """
        # Creating a test Feed
        feed = Feed.objects.create(
            name="Test Feed",
            active=True,
            description="This is a test feed",
        )

        # DELETE the Feed
        response = self.client.delete(f"/api/administration/feed/{feed.id}/")

        # Assertions for a successful deletion (status code 204)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assertions to check the object is deleted from the database
        with self.assertRaises(Feed.DoesNotExist):
            feed.refresh_from_db()

    # --------------------------------------------------END-FEED-----------------------------------------------------------

    def test_list_priorities(self):
        """
        Test API Priority listing
        """
        # Create some test Priority objects
        priorities = [
            Priority.objects.create(
                name="Test Priority",
                severity=10,
                attend_time=timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT),
                solve_time=timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT),
                notification_amount=3,
                color="#FFFFFF",
            ),
        ]

        # GET the list of priorities
        response = self.client.get("/api/administration/priority/")

        # Assertions for a successful listing (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assertions to check the list number equals to # of db objects
        response_data = response.data
        self.assertEqual(response_data["count"], Priority.objects.count())

    def test_create_priority(self):
        """
        Test API Priority creation
        """
        # Simulating POST data
        priority_data = {
            "name": "Test Priority",
            "severity": 7,
            "attend_time": "00:00:00",
            "solve_time": "01:00:00",
            "notification_amount": 4,
            "color": "#FF0000",
        }

        # POST the data
        response = self.client.post(
            "/api/administration/priority/", priority_data, format="json"
        )

        # Assertions for a successful creation (status code 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_priority(self):
        """
        Test API Priority update
        """
        # Creating a test Priority
        priority = Priority.objects.create(
            name="Test Priority",
            severity=7,
            attend_time=timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT),
            solve_time=timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT),
            notification_amount=4,
            color="#FF0000",
        )

        # Updated data for the Priority
        updated_data = {
            "name": "Updated Priority",
            "severity": 11,
            "attend_time": "00:30:00",
            "solve_time": "02:00:00",
            "notification_amount": 5,
            "color": "#00FF00",
        }

        # PUT the data
        response = self.client.put(
            f"/api/administration/priority/{priority.id}/", updated_data, format="json"
        )

        # Assertions for a successful update (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assertions to check the object is updated in the database
        priority.refresh_from_db()
        self.assertEqual(priority.name, "Updated Priority")

    def test_delete_priority(self):
        """
        Test API Priority deletion
        """
        # Creating a test Priority
        priority = Priority.objects.create(
            name="Test Priority",
            severity=9,
            attend_time=timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT),
            solve_time=timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT),
            notification_amount=4,
            color="#FF0000",
        )

        # DELETE the Priority
        response = self.client.delete(f"/api/administration/priority/{priority.id}/")

        # Assertions for a successful deletion (status code 204)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assertions to check the object is deleted from the database
        with self.assertRaises(Priority.DoesNotExist):
            priority.refresh_from_db()
