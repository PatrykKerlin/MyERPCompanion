from django.db import models

from .base_model import BaseModel


class History(BaseModel):
    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'History'

    class ModificationTypes(models.TextChoices):
        UPDATE = 'update', 'update'
        DELETE = 'delete', 'delete'

    table_name = models.CharField(max_length=50)
    record_id = models.IntegerField()
    modification_type = models.CharField(max_length=6, choices=ModificationTypes.choices)
    data = models.JSONField()

    def __str__(self):
        return f"History record for {self.table_name} at {self.modified_at}"
