from django.db import models

from base.models.base_model import BaseModel
from ..managers.language_manager import LanguageManager


class Language(BaseModel):
    objects = LanguageManager()

    language_id = models.IntegerField()

    name = models.CharField(max_length=25)
    value = models.CharField(max_length=2)

    def __str__(self):
        return self.name
