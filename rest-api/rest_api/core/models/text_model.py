from django.db import models

from base.models.base_model import BaseModel
from base.models.base_languages_model import BaseLanguagesModel
from ..managers.text_manager import TextManager


class Text(BaseModel, BaseLanguagesModel):
    objects = TextManager()

    text_id = models.IntegerField()

    language = models.CharField(max_length=2, choices=BaseLanguagesModel.Languages.choices)
    value = models.TextField()

    def __str__(self):
        value_str = str(self.value)
        return f'{self.language}: {value_str[:10]}{"..." if len(value_str) > 10 else ""}'
