from django.core.management.base import BaseCommand
from django.db.utils import OperationalError as DjangoOperationalError
from redis import ConnectionError as RedisConnectionError
import redis
import time


class Command(BaseCommand):

    def handle(self, *args, **options):
        redis_ready = False

        self.stdout.write(self.style.WARNING('Waiting for Redis database...'))

        while not redis_ready:
            try:
                redis_connection = redis.StrictRedis(host='redis', port=6379, db=0)
                redis_connection.ping()
                redis_ready = True
            except (DjangoOperationalError, RedisConnectionError):
                self.stdout.write(self.style.WARNING('Redis database unavailable, waiting 1 second...'))
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Redis database available!'))
