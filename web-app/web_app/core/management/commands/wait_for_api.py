import time
import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from ...helpers.constants import ApiEndpoints


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = settings.API_URL + ApiEndpoints.HEALTH_CHECK
        api_ready = False

        self.stdout.write(self.style.WARNING('Waiting for REST API...'))

        while not api_ready:
            try:
                response = requests.get(url)
                if response.status_code == 200 and response.json().get('healthy') is True:
                    api_ready = True
                else:
                    self.stdout.write(self.style.WARNING('REST API unavailable, waiting 1 second...'))
            except requests.ConnectionError:
                self.stdout.write(self.style.WARNING('REST API unavailable, waiting 1 second...'))

            time.sleep(1)

        self.stdout.write(self.style.SUCCESS('REST API available!'))
