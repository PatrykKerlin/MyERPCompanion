from django.db import models

from base.models import BaseModel
from ..managers.generic_manager import GenericManager


class Language(BaseModel):
    objects = GenericManager()

    language_id = models.IntegerField()

    name = models.CharField(max_length=25)
    value = models.CharField(max_length=2)

    def __str__(self):
        return self.name
