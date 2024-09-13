from django.db.models import Manager


class BaseManager(Manager):
    pass
    # def get_queryset(self):
    #     return super().get_queryset().filter(is_active=True)
