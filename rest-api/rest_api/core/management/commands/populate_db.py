from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        is_populated = False
        user = get_user_model()

        if user.objects.count() == 0:
            user.objects.create_superuser(
                username='admin',
                password='admin',
            )
            is_populated = True

        if is_populated:
            self.stdout.write(self.style.SUCCESS("Database populated with initial data!"))
