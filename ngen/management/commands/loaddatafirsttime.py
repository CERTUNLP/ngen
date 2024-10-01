from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.utils import IntegrityError
from ngen.models import User


class Command(BaseCommand):
    help = "Same as loaddata, but only runs if the User table is empty."

    def handle(self, *args, **kwargs):

        if User.objects.exists():
            self.stdout.write(
                self.style.WARNING("User data already exists. Skipping loaddata.")
            )
        else:
            try:
                call_command("loaddata", *args, **kwargs)
                self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
