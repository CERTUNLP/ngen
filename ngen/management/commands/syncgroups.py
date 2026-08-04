import json
import os

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

WRITE_ACTIONS = ("add", "change", "delete")


class Command(BaseCommand):
    help = (
        "Reconciles the groups and their permissions with the ones defined in "
        "ngen/fixtures/group.json. The fixture is only loaded on a brand new "
        "installation, so the permissions a release adds to a role never reach "
        "the installations already running. Unlike 'loaddata group' this is "
        "additive: it grants what is missing and does not touch anything else, "
        "so the permissions an administrator added by hand are kept."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            help="Path of the fixture to read (defaults to the one shipped with ngen)",
        )
        parser.add_argument(
            "--group",
            action="append",
            dest="groups",
            help="Only this group, can be repeated",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without applying it",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Exit with 1 if there is anything to apply, implies --dry-run",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Also revoke the permissions the fixture does not define",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"] or options["check"]
        groups_filter = options["groups"]

        entries = self.read_fixture(options["fixture"])
        if groups_filter:
            entries = [e for e in entries if e["name"] in groups_filter]
            missing = set(groups_filter) - {e["name"] for e in entries}
            if missing:
                raise CommandError(
                    f"The fixture has no group named {', '.join(sorted(missing))}"
                )

        pending = 0
        for entry in entries:
            pending += self.sync_group(entry, dry_run=dry_run, prune=options["prune"])

        self.report_unusable_permissions([entry["name"] for entry in entries])

        if not pending:
            self.stdout.write(self.style.SUCCESS("Every group is already in sync."))
        elif dry_run:
            self.stdout.write(
                self.style.WARNING(f"{pending} change(s) pending, nothing was applied.")
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"{pending} change(s) applied."))

        if options["check"] and pending:
            raise SystemExit(1)

    def read_fixture(self, path):
        """
        Groups of the fixture as {name, permissions}, resolving the permissions
        to the ones existing in the database
        """
        path = path or os.path.join(
            apps.get_app_config("ngen").path, "fixtures", "group.json"
        )
        try:
            with open(path, encoding="utf-8") as fixture:
                data = json.load(fixture)
        except OSError as error:
            raise CommandError(f"Could not read {path}: {error}") from error

        entries = []
        for obj in data:
            if obj.get("model") != "auth.group":
                continue
            permissions, unknown = self.resolve_permissions(
                obj["fields"].get("permissions", [])
            )
            for codename in unknown:
                self.stdout.write(
                    self.style.WARNING(
                        f"  the fixture asks for '{codename}', which does not exist "
                        "in this installation"
                    )
                )
            entries.append({"name": obj["fields"]["name"], "permissions": permissions})
        return entries

    @staticmethod
    def resolve_permissions(natural_keys):
        permissions, unknown = [], []
        for codename, app_label, model in natural_keys:
            permission = Permission.objects.filter(
                codename=codename,
                content_type__app_label=app_label,
                content_type__model=model,
            ).first()
            if permission:
                permissions.append(permission)
            else:
                unknown.append(codename)
        return permissions, unknown

    def sync_group(self, entry, dry_run, prune):
        """
        Grant the permissions of the fixture the group does not have, and revoke
        the ones it has beyond it only when pruning. Returns how many changed.
        """
        group, created = (
            Group.objects.get_or_create(name=entry["name"])
            if not dry_run
            else (Group.objects.filter(name=entry["name"]).first(), False)
        )
        if group is None:
            self.stdout.write(self.style.MIGRATE_HEADING(entry["name"]))
            self.stdout.write(
                f"  + would be created with {len(entry['permissions'])} permission(s)"
            )
            return len(entry["permissions"])

        current = set(group.permissions.all())
        expected = set(entry["permissions"])
        to_add = sorted(expected - current, key=lambda p: p.codename)
        to_remove = (
            sorted(current - expected, key=lambda p: p.codename) if prune else []
        )

        if not (created or to_add or to_remove):
            return 0

        self.stdout.write(self.style.MIGRATE_HEADING(entry["name"]))
        if created:
            self.stdout.write("  + created")
        for permission in to_add:
            self.stdout.write(self.style.SUCCESS(f"  + {permission.codename}"))
        for permission in to_remove:
            self.stdout.write(self.style.ERROR(f"  - {permission.codename}"))

        if not dry_run:
            with transaction.atomic():
                group.permissions.add(*to_add)
                if to_remove:
                    group.permissions.remove(*to_remove)

        return len(to_add) + len(to_remove)

    def report_unusable_permissions(self, group_names):
        """
        DRF maps GET to view_<model>, so a group that can add, change or delete a
        model without being able to view it cannot use those permissions through
        the API. It is worth saying, it is how the Incident Responder role ended
        up unable to read the playbooks it was meant to run.
        """
        for name in group_names:
            group = Group.objects.filter(name=name).first()
            if not group:
                continue

            actions = {}
            # Only the models of ngen: the ones of the packages it depends on are
            # not served by its api, so the mapping does not apply to them
            for permission in group.permissions.filter(
                content_type__app_label="ngen"
            ).select_related("content_type"):
                action, _, model = permission.codename.partition("_")
                if action in WRITE_ACTIONS + ("view",) and model:
                    actions.setdefault(model, set()).add(action)

            unusable = sorted(
                model
                for model, done in actions.items()
                if "view" not in done and done & set(WRITE_ACTIONS)
            )
            if unusable:
                self.stdout.write(
                    self.style.WARNING(
                        f"{name}: can write but not read {len(unusable)} model(s), "
                        "so those permissions cannot be used through the api: "
                        f"{', '.join(unusable)}"
                    )
                )
