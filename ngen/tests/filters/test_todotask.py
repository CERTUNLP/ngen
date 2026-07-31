"""
Django TodoTask filter tests. Tests search_fields and filterset_class.
"""

import pytz
from django.utils import timezone

from ngen.filters import TodoTaskFilter
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
from ngen.tests.filters.base_filter_test import BaseFilterTest


class TodoTaskFilterTest(BaseFilterTest):
    """
    TodoTask filter test class.
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/network_entity.json",
        "tests/network.json",
        "tests/contact.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "todo"
        super().setUpTestData()

        priority = Priority.objects.get(slug="high")
        tlp = Tlp.objects.get(slug="green")
        feed = Feed.objects.get(slug="csirtamericas")
        cls.user = User.objects.get(username="ngen")

        taxonomy_1 = Taxonomy.objects.get(slug="phishing")
        taxonomy_2 = Taxonomy.objects.get(slug="copyright")

        cls.playbook_1 = Playbook.objects.create(name="Phishing playbook")
        cls.playbook_1.taxonomy.set([taxonomy_1])
        cls.task_1 = Task.objects.create(
            name="Identify phishing email", playbook=cls.playbook_1, priority=priority
        )

        cls.playbook_2 = Playbook.objects.create(name="Copyright playbook")
        cls.playbook_2.taxonomy.set([taxonomy_2])
        cls.task_2 = Task.objects.create(
            name="Check the complaint", playbook=cls.playbook_2, priority=priority
        )

        def create_event(taxonomy):
            return Event.objects.create(
                domain="info.unlp.edu.ar",
                taxonomy=taxonomy,
                feed=feed,
                tlp=tlp,
                reporter=cls.user,
                priority=priority,
            )

        cls.event_1 = create_event(taxonomy_1)
        cls.event_2 = create_event(taxonomy_2)

        cls.todo_1 = cls.event_1.todos.get()
        cls.todo_1.completed = True
        cls.todo_1.note = "Malicious email already taken down"
        cls.todo_1.assigned_to = cls.user
        cls.todo_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.todo_1.save()

        cls.todo_2 = cls.event_2.todos.get()

        cls.queryset = TodoTask.objects.all()

        cls.filter = lambda query_params: TodoTaskFilter(
            query_params, queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by note
        query = "taken down"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]), self.todo_1.id
        )

        # Searching by task name
        query = "complaint"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]), self.todo_2.id
        )

        # Searching by assigned user username
        query = self.user.username
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]), self.todo_1.id
        )

        # Searching with no results
        query = "no results"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_id(self):
        """
        Test filter by id.
        """

        params = {"id": self.todo_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02",
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_1])

    def test_filter_by_event(self):
        """
        Test filter by event.
        """

        params = {"event": self.event_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_1])

    def test_filter_by_task(self):
        """
        Test filter by task.
        """

        params = {"task": self.task_2.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_2])

    def test_filter_by_playbook(self):
        """
        Test filter by the playbook of the task.
        """

        params = {"task__playbook": self.playbook_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_1])

    def test_filter_by_completed(self):
        """
        Test filter by completed.
        """

        params = {"completed": True}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_1])

    def test_filter_by_assigned_to(self):
        """
        Test filter by assigned user.
        """

        params = {"assigned_to": self.user.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.todo_1])
