from django.db.models import Manager


class BaseManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
