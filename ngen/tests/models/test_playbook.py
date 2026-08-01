"""
Django Playbook, Task and TodoTask model tests.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

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


class PlaybookTestCase(TestCase):
    """
    This will handle Playbook, Task and TodoTask model testcases
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
        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.user = User.objects.get(username="ngen")
        cls.taxonomy = Taxonomy.objects.get(slug="phishing")
        cls.other_taxonomy = Taxonomy.objects.get(slug="copyright")

        cls.playbook = Playbook.objects.create(name="Phishing playbook")
        cls.playbook.taxonomy.set([cls.taxonomy])
        cls.task_1 = Task.objects.create(
            name="Identify phishing email",
            playbook=cls.playbook,
            priority=cls.priority,
        )
        cls.task_2 = Task.objects.create(
            name="Notify the affected user",
            playbook=cls.playbook,
            priority=cls.priority,
        )

        cls.other_playbook = Playbook.objects.create(name="Copyright playbook")
        cls.other_playbook.taxonomy.set([cls.other_taxonomy])
        cls.other_task = Task.objects.create(
            name="Check the complaint",
            playbook=cls.other_playbook,
            priority=cls.priority,
        )

    def _create_event(self, taxonomy=None):
        return Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=taxonomy or self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            priority=self.priority,
        )

    def test_playbook_tasks(self):
        """
        Test that the tasks of a playbook are related to it
        """
        self.assertQuerysetEqual(
            self.playbook.tasks.all(), [self.task_1, self.task_2], ordered=False
        )

    def test_event_creation_assigns_todos(self):
        """
        Test that a new event gets a todo for every task of the playbooks of
        its taxonomy
        """
        event = self._create_event()

        self.assertEqual(event.todos.count(), 2)
        self.assertQuerysetEqual(
            Task.objects.filter(todos__event=event),
            [self.task_1, self.task_2],
            ordered=False,
        )

    def test_event_creation_without_playbook_assigns_no_todos(self):
        """
        Test that an event whose taxonomy has no playbook gets no todos
        """
        taxonomy = Taxonomy.objects.get(slug="malware")
        event = self._create_event(taxonomy=taxonomy)

        self.assertEqual(event.todos.count(), 0)

    def test_event_taxonomy_change_reassigns_todos(self):
        """
        Test that changing the taxonomy of an event replaces its todos with the
        ones of the playbooks of the new taxonomy
        """
        event = self._create_event()
        self.assertEqual(event.todos.count(), 2)

        event.taxonomy = self.other_taxonomy
        event.save()

        self.assertQuerysetEqual(
            Task.objects.filter(todos__event=event), [self.other_task]
        )

    def test_import_playbook_tasks_assigns_the_missing_ones(self):
        """
        Test that a playbook written after the event reaches it when its tasks
        are imported
        """
        event = self._create_event(taxonomy=Taxonomy.objects.get(slug="malware"))
        self.assertEqual(event.todos.count(), 0)

        playbook = Playbook.objects.create(name="Malware playbook")
        playbook.taxonomy.set([event.taxonomy])
        task = Task.objects.create(
            name="Isolate the host", playbook=playbook, priority=self.priority
        )

        self.assertEqual(event.import_playbook_tasks(), 1)
        self.assertQuerysetEqual(Task.objects.filter(todos__event=event), [task])

    def test_import_playbook_tasks_does_not_duplicate(self):
        """
        Test that importing twice does not assign the same task again
        """
        event = self._create_event()
        self.assertEqual(event.todos.count(), 2)

        self.assertEqual(event.import_playbook_tasks(), 0)
        self.assertEqual(event.todos.count(), 2)

    def test_import_playbook_tasks_keeps_the_work_already_done(self):
        """
        Test that importing does not touch the todos already completed
        """
        event = self._create_event()
        todo = event.todos.get(task=self.task_1)
        todo.completed = True
        todo.note = "Already done"
        todo.save()

        new_task = Task.objects.create(
            name="Close the case", playbook=self.playbook, priority=self.priority
        )

        self.assertEqual(event.import_playbook_tasks(), 1)

        todo.refresh_from_db()
        self.assertTrue(todo.completed)
        self.assertEqual(todo.note, "Already done")
        self.assertIsNotNone(todo.completed_date)
        self.assertTrue(event.todos.filter(task=new_task).exists())

    def test_todo_completion_sets_completed_date(self):
        """
        Test that completing a todo sets its completed date
        """
        todo = self._create_event().todos.first()
        self.assertIsNone(todo.completed_date)

        todo.completed = True
        todo.save()

        self.assertIsNotNone(todo.completed_date)

    def test_todo_completed_date_is_not_overwritten(self):
        """
        Test that the completed date of an already completed todo is kept on
        later updates
        """
        todo = self._create_event().todos.first()
        todo.completed = True
        todo.save()
        completed_date = todo.completed_date

        todo.note = "Some note"
        todo.save()

        self.assertEqual(todo.completed_date, completed_date)

    def test_todo_uncompletion_clears_completed_date(self):
        """
        Test that un-completing a todo clears its completed date
        """
        todo = self._create_event().todos.first()
        todo.completed = True
        todo.save()
        self.assertIsNotNone(todo.completed_date)

        todo.completed = False
        todo.save()

        self.assertIsNone(todo.completed_date)

    def test_todo_is_unique_by_task_and_event(self):
        """
        Test that a task cannot be assigned twice to the same event
        """
        event = self._create_event()

        with self.assertRaises(ValidationError):
            TodoTask(task=self.task_1, event=event).save()

    def test_todo_deletion_on_task_deletion(self):
        """
        Test that the todos of a task are deleted with it
        """
        event = self._create_event()
        self.assertEqual(event.todos.count(), 2)

        self.task_1.delete()

        self.assertEqual(event.todos.count(), 1)
        self.assertFalse(TodoTask.objects.filter(task_id=self.task_1.pk).exists())
