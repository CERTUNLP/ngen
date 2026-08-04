"""
Django syncgroups management command tests.
"""

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.contrib.auth.models import Group, Permission
from django.core.management import CommandError, call_command
from django.test import TestCase


class SyncGroupsCommandTestCase(TestCase):
    """
    This will handle the syncgroups command testcases
    """

    @classmethod
    def setUpTestData(cls):
        cls.view_playbook = Permission.objects.get(
            codename="view_playbook", content_type__app_label="ngen"
        )
        cls.change_playbook = Permission.objects.get(
            codename="change_playbook", content_type__app_label="ngen"
        )
        cls.view_task = Permission.objects.get(
            codename="view_task", content_type__app_label="ngen"
        )

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def write_fixture(self, groups):
        """
        Fixture with the same shape as ngen/fixtures/group.json
        """
        path = Path(self.tempdir.name) / "group.json"
        path.write_text(
            json.dumps(
                [
                    {
                        "model": "auth.group",
                        "pk": position,
                        "fields": {
                            "name": name,
                            "permissions": [
                                [
                                    permission.codename,
                                    "ngen",
                                    permission.content_type.model,
                                ]
                                for permission in permissions
                            ],
                        },
                    }
                    for position, (name, permissions) in enumerate(
                        groups.items(), start=1
                    )
                ]
            ),
            encoding="utf-8",
        )
        return str(path)

    def call(self, fixture, *args):
        out = StringIO()
        call_command("syncgroups", "--fixture", fixture, *args, stdout=out)
        return out.getvalue()

    def test_grants_the_missing_permissions(self):
        """
        Test that the permissions of the fixture the group does not have are granted
        """
        group = Group.objects.create(name="Responder")
        group.permissions.add(self.change_playbook)
        fixture = self.write_fixture(
            {"Responder": [self.change_playbook, self.view_playbook]}
        )

        output = self.call(fixture)

        self.assertIn("view_playbook", output)
        self.assertQuerysetEqual(
            group.permissions.all(),
            [self.change_playbook, self.view_playbook],
            ordered=False,
        )

    def test_keeps_the_permissions_added_by_the_administrator(self):
        """
        Test that it does not revoke anything, which is what tells it apart from
        loaddata: a permission granted by hand survives
        """
        group = Group.objects.create(name="Responder")
        group.permissions.add(self.change_playbook, self.view_task)
        fixture = self.write_fixture({"Responder": [self.change_playbook]})

        self.call(fixture)

        self.assertIn(self.view_task, group.permissions.all())

    def test_prune_revokes_what_the_fixture_does_not_define(self):
        """
        Test that pruning does revoke them, which is opt in
        """
        group = Group.objects.create(name="Responder")
        group.permissions.add(self.change_playbook, self.view_task)
        fixture = self.write_fixture({"Responder": [self.change_playbook]})

        output = self.call(fixture, "--prune")

        self.assertIn("- view_task", output)
        self.assertQuerysetEqual(group.permissions.all(), [self.change_playbook])

    def test_dry_run_changes_nothing(self):
        """
        Test that a dry run only reports
        """
        group = Group.objects.create(name="Responder")
        fixture = self.write_fixture({"Responder": [self.view_playbook]})

        output = self.call(fixture, "--dry-run")

        self.assertIn("view_playbook", output)
        self.assertIn("nothing was applied", output)
        self.assertEqual(group.permissions.count(), 0)

    def test_check_exits_with_an_error_when_there_is_something_to_apply(self):
        """
        Test the mode meant for CI
        """
        group = Group.objects.create(name="Responder")
        fixture = self.write_fixture({"Responder": [self.view_playbook]})

        with self.assertRaises(SystemExit):
            self.call(fixture, "--check")

        self.assertEqual(group.permissions.count(), 0)

        group.permissions.add(self.view_playbook)
        self.call(fixture, "--check")

    def test_creates_a_group_that_does_not_exist(self):
        """
        Test that a group added by a release is created
        """
        fixture = self.write_fixture({"Brand new": [self.view_playbook]})

        self.call(fixture)

        self.assertQuerysetEqual(
            Group.objects.get(name="Brand new").permissions.all(), [self.view_playbook]
        )

    def test_only_the_given_group(self):
        """
        Test that --group limits the reconciliation
        """
        first = Group.objects.create(name="Responder")
        second = Group.objects.create(name="Analist")
        fixture = self.write_fixture(
            {"Responder": [self.view_playbook], "Analist": [self.view_task]}
        )

        self.call(fixture, "--group", "Responder")

        self.assertEqual(first.permissions.count(), 1)
        self.assertEqual(second.permissions.count(), 0)

    def test_unknown_group_is_an_error(self):
        """
        Test that asking for a group the fixture does not define fails
        """
        fixture = self.write_fixture({"Responder": [self.view_playbook]})

        with self.assertRaises(CommandError):
            self.call(fixture, "--group", "Does not exist")

    def test_reports_the_permissions_that_cannot_be_used(self):
        """
        Test the report of write permissions without their view counterpart,
        which DRF needs to answer a GET
        """
        group = Group.objects.create(name="Responder")
        group.permissions.add(self.change_playbook)
        fixture = self.write_fixture({"Responder": [self.change_playbook]})

        output = self.call(fixture)

        self.assertIn("can write but not read", output)
        self.assertIn("playbook", output)

    def test_reports_nothing_when_every_write_has_its_view(self):
        """
        Test that the report stays quiet when there is nothing to say
        """
        group = Group.objects.create(name="Responder")
        group.permissions.add(self.change_playbook, self.view_playbook)
        fixture = self.write_fixture(
            {"Responder": [self.change_playbook, self.view_playbook]}
        )

        output = self.call(fixture)

        self.assertNotIn("can write but not read", output)
        self.assertIn("already in sync", output)
