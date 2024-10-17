from django.db import models

from base.models.base_model import BaseModel
from base.models.base_languages_model import BaseLanguagesModel
from ..managers.translation_manager import TranslationManager


class Translation(BaseModel, BaseLanguagesModel):
    objects = TranslationManager()

    translation_id = models.IntegerField()

    language = models.CharField(max_length=2, choices=BaseLanguagesModel.Languages.choices)
    value = models.CharField()

    def __str__(self):
        value_str = str(self.value)
        return f'{self.language}: {value_str[:10]}{"..." if len(value_str) > 10 else ""}'
