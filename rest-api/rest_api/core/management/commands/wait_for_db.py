from django.core.management.base import BaseCommand
from django.db.utils import OperationalError as DjangoOperationalError
from psycopg2 import OperationalError as Psycopg2OperationalError
import time

class Command(BaseCommand):

    def handle(self, *args, **options):
        db_ready = False

        self.stdout.write(self.style.WARNING('Waiting for database...'))

        while not db_ready:
            try:
                self.check(databases=['default'])
                db_ready = True
            except (DjangoOperationalError, Psycopg2OperationalError):
                self.stdout.write(self.style.WARNING('Database unavailable, waiting 1 second...'))
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))

