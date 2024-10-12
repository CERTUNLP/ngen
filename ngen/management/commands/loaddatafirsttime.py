from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import IntegrityError
from ngen.models import User


class Command(BaseCommand):
    help = "Same as loaddata, but only runs if the User table is empty."

    def add_arguments(self, parser):
        parser.add_argument("fixtures", nargs="+", help="List of fixture files to load")

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(
                self.style.WARNING("User data already exists. Skipping loaddata.")
            )
        else:
            try:
                fixtures = options["fixtures"]
                call_command("loaddata", *fixtures)
                self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
            except CommandError as e:
                self.stdout.write(self.style.ERROR(f"Command error: {e}"))
