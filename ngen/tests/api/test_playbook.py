"""
Django Playbook, Task and TodoTask API tests.
"""

from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status

from ngen.models import (
    Event,
    Feed,
    Playbook,
    Priority,
    Task,
    Taxonomy,
    Tlp,
    TodoTask,
    User,
)
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class PlaybookAPITestCase(APITestCaseWithLogin):
    """
    This will handle Playbook, Task and TodoTask API testcases
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/report.json",
        "tests/network_entity.json",
        "tests/network.json",
        "tests/contact.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.base_url = "http://testserver"
        cls.url_playbook_list = reverse("playbook-list")
        cls.url_task_list = reverse("task-list")
        cls.url_todo_list = reverse("todo-list")
        cls.url_event_list = reverse("event-list")
        cls.url_playbook_detail = lambda pk: reverse(
            "playbook-detail", kwargs={"pk": pk}
        )
        cls.url_todo_detail = lambda pk: reverse("todo-detail", kwargs={"pk": pk})

        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.user = User.objects.get(username="ngen")
        cls.taxonomy = Taxonomy.objects.get(slug="phishing")
        cls.other_taxonomy = Taxonomy.objects.get(slug="copyright")

        cls.priority_url = cls.base_url + reverse(
            "priority-detail", kwargs={"pk": cls.priority.pk}
        )
        cls.tlp_url = cls.base_url + reverse("tlp-detail", kwargs={"pk": cls.tlp.pk})
        cls.feed_url = cls.base_url + reverse("feed-detail", kwargs={"pk": cls.feed.pk})
        cls.taxonomy_url = cls.base_url + reverse(
            "taxonomy-detail", kwargs={"pk": cls.taxonomy.pk}
        )
        cls.user_url = cls.base_url + reverse("user-detail", kwargs={"pk": cls.user.pk})

        # Playbook with two tasks, matching the 'phishing' taxonomy
        cls.playbook = Playbook.objects.create(name="Phishing playbook")
        cls.playbook.taxonomy.set([cls.taxonomy])
        cls.task_1 = Task.objects.create(
            name="Identify phishing email",
            description="Find the original email",
            playbook=cls.playbook,
            priority=cls.priority,
        )
        # Less severe than task_1, so the playbook order can be asserted
        cls.task_2 = Task.objects.create(
            name="Notify the affected user",
            description="Send the notification",
            playbook=cls.playbook,
            priority=Priority.objects.get(slug="low"),
        )

    def _create_event(self, taxonomy=None):
        """
        Helper that creates an event, which assigns the todos of the
        playbooks of its taxonomy
        """
        return Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=taxonomy or self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            priority=self.priority,
        )

    def test_playbook_post_with_tasks(self):
        """
        This will test successful Playbook POST and Task POST on that playbook
        """
        response = self.client.post(
            self.url_playbook_list,
            data={"name": "Copyright playbook", "taxonomy": [self.taxonomy_url]},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        playbook_url = response.data["url"]
        playbook = Playbook.objects.get(name="Copyright playbook")
        self.assertQuerysetEqual(playbook.taxonomy.all(), [self.taxonomy])

        for name in ["Check the complaint", "Notify the network admin"]:
            response = self.client.post(
                self.url_task_list,
                data={
                    "name": name,
                    "description": f"{name} description",
                    "priority": self.priority_url,
                    "playbook": playbook_url,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(playbook.tasks.count(), 2)

        # The tasks are exposed on the playbook detail
        response = self.client.get(self.url_playbook_detail(playbook.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tasks"]), 2)

    def test_event_post_assigns_playbook_todos(self):
        """
        This will test that a new event gets a todo for every task of the
        playbooks of its taxonomy
        """
        response = self.client.post(
            self.url_event_list,
            data={
                "domain": "info.unlp.edu.ar",
                "priority": self.priority_url,
                "tlp": self.tlp_url,
                "taxonomy": self.taxonomy_url,
                "feed": self.feed_url,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["todos"]), 2)

        event = Event.objects.get(pk=response.data["url"].rstrip("/").split("/")[-1])
        self.assertQuerysetEqual(
            Task.objects.filter(todos__event=event),
            [self.task_1, self.task_2],
            ordered=False,
        )
        self.assertFalse(event.todos.filter(completed=True).exists())

    def test_event_post_without_playbook_has_no_todos(self):
        """
        This will test that an event whose taxonomy has no playbook gets no todos
        """
        response = self.client.post(
            self.url_event_list,
            data={
                "domain": "info.unlp.edu.ar",
                "priority": self.priority_url,
                "tlp": self.tlp_url,
                "taxonomy": self.base_url
                + reverse("taxonomy-detail", kwargs={"pk": self.other_taxonomy.pk}),
                "feed": self.feed_url,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["todos"], [])

    def test_todo_get_list(self):
        """
        This will test successful TodoTask GET list
        """
        self._create_event()

        response = self.client.get(self.url_todo_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_todo_get_detail(self):
        """
        This will test successful TodoTask GET detail
        """
        event = self._create_event()
        todo = event.todos.first()

        response = self.client.get(self.url_todo_detail(todo.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["url"],
            self.base_url + self.url_todo_detail(todo.pk),
        )
        self.assertEqual(
            response.data["task"],
            self.base_url + reverse("task-detail", kwargs={"pk": todo.task.pk}),
        )
        self.assertEqual(
            response.data["event"],
            self.base_url + reverse("event-detail", kwargs={"pk": event.pk}),
        )
        self.assertFalse(response.data["completed"])
        self.assertIsNone(response.data["completed_date"])
        self.assertIsNone(response.data["assigned_to"])

    def test_todo_get_list_filtered_by_event(self):
        """
        This will test TodoTask GET list filtered by event
        """
        event = self._create_event()
        self._create_event(taxonomy=self.other_taxonomy)

        response = self.client.get(f"{self.url_todo_list}?event={event.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            {result["event"] for result in response.data["results"]},
            {self.base_url + reverse("event-detail", kwargs={"pk": event.pk})},
        )

    def test_todo_get_list_ordered_by_task_priority(self):
        """
        This will test TodoTask GET list ordered by the priority of its task,
        which is the order the playbook gives to its tasks
        """
        event = self._create_event()

        response = self.client.get(
            f"{self.url_todo_list}?event={event.pk}&ordering=task__priority__severity"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [result["task"] for result in response.data["results"]],
            [
                self.base_url + reverse("task-detail", kwargs={"pk": self.task_1.pk}),
                self.base_url + reverse("task-detail", kwargs={"pk": self.task_2.pk}),
            ],
        )

        response = self.client.get(
            f"{self.url_todo_list}?event={event.pk}&ordering=-task__priority__severity"
        )
        self.assertEqual(
            [result["task"] for result in response.data["results"]],
            [
                self.base_url + reverse("task-detail", kwargs={"pk": self.task_2.pk}),
                self.base_url + reverse("task-detail", kwargs={"pk": self.task_1.pk}),
            ],
        )

    def test_todo_patch(self):
        """
        This will test successful TodoTask PATCH and that the change is reflected
        """
        event = self._create_event()
        todo = event.todos.first()

        response = self.client.patch(
            self.url_todo_detail(todo.pk),
            data={
                "completed": True,
                "note": "Already reported to the network admin",
                "assigned_to": self.user_url,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        todo.refresh_from_db()
        self.assertTrue(todo.completed)
        self.assertIsNotNone(todo.completed_date)
        self.assertEqual(todo.note, "Already reported to the network admin")
        self.assertEqual(todo.assigned_to, self.user)

        response = self.client.get(self.url_todo_detail(todo.pk))
        self.assertTrue(response.data["completed"])
        self.assertEqual(response.data["note"], "Already reported to the network admin")
        self.assertEqual(response.data["assigned_to"], self.user_url)

    def test_todo_patch_uncompleted_clears_completed_date(self):
        """
        This will test that un-completing a TodoTask clears its completed date
        """
        event = self._create_event()
        todo = event.todos.first()
        todo.completed = True
        todo.save()
        self.assertIsNotNone(todo.completed_date)

        response = self.client.patch(
            self.url_todo_detail(todo.pk), data={"completed": False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["completed_date"])

        todo.refresh_from_db()
        self.assertIsNone(todo.completed_date)

    def test_todo_patch_does_not_change_task_nor_event(self):
        """
        This will test that task and event are read only on TodoTask PATCH
        """
        event = self._create_event()
        other_event = self._create_event(taxonomy=self.other_taxonomy)
        todo = event.todos.get(task=self.task_1)

        response = self.client.patch(
            self.url_todo_detail(todo.pk),
            data={
                "event": self.base_url
                + reverse("event-detail", kwargs={"pk": other_event.pk}),
                "task": self.base_url
                + reverse("task-detail", kwargs={"pk": self.task_2.pk}),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        todo.refresh_from_db()
        self.assertEqual(todo.event, event)
        self.assertEqual(todo.task, self.task_1)

    def test_task_move(self):
        """
        This will test the action that moves a task within its playbook
        """
        url = reverse("task-move", kwargs={"pk": self.task_2.pk})

        response = self.client.post(url, data={"direction": "up"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["moved"])
        self.assertQuerysetEqual(self.playbook.tasks.all(), [self.task_2, self.task_1])

        # The first one cannot go further up
        response = self.client.post(url, data={"direction": "up"}, format="json")
        self.assertFalse(response.data["moved"])

    def test_task_move_needs_a_direction(self):
        """
        This will test that the move action rejects an unknown direction
        """
        response = self.client.post(
            reverse("task-move", kwargs={"pk": self.task_1.pk}),
            data={"direction": "sideways"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_task_move_needs_permission(self):
        """
        This will test that moving a task needs change_task
        """
        user = User.objects.create(
            username="without_permissions", password="test", priority=self.priority
        )
        user.user_permissions.set(Permission.objects.filter(codename="view_task"))
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("task-move", kwargs={"pk": self.task_1.pk}),
            data={"direction": "up"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_import_playbook_tasks(self):
        """
        This will test the action that assigns the tasks of the playbooks of the
        taxonomy that the event does not have yet
        """
        event = self._create_event(taxonomy=self.other_taxonomy)
        self.assertEqual(event.todos.count(), 0)

        # A playbook written after the event
        playbook = Playbook.objects.create(name="Copyright playbook")
        playbook.taxonomy.set([self.other_taxonomy])
        task = Task.objects.create(
            name="Check the complaint", playbook=playbook, priority=self.priority
        )

        url = reverse("event-import_playbook_tasks", kwargs={"pk": event.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["imported"], 1)
        self.assertQuerysetEqual(Task.objects.filter(todos__event=event), [task])

        # Importing again assigns nothing
        response = self.client.post(url)
        self.assertEqual(response.data["imported"], 0)
        self.assertEqual(event.todos.count(), 1)

    def test_event_import_playbook_tasks_needs_permission(self):
        """
        This will test that importing the tasks of a playbook needs add_todotask
        """
        event = self._create_event()
        user = User.objects.create(
            username="without_permissions", password="test", priority=self.priority
        )
        user.user_permissions.set(
            Permission.objects.filter(codename__in=["view_event", "view_todotask"])
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("event-import_playbook_tasks", kwargs={"pk": event.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_todo_delete(self):
        """
        This will test successful TodoTask DELETE
        """
        event = self._create_event()
        todo = event.todos.first()

        response = self.client.delete(self.url_todo_detail(todo.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TodoTask.objects.filter(pk=todo.pk).exists())
        self.assertEqual(event.todos.count(), 1)
