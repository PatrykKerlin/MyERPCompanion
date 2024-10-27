from django.db import models

from base.models.base_model import BaseModel
from .language_model import Language
from ..managers.translation_manager import TranslationManager


class Translation(BaseModel):
    objects = TranslationManager()

    translation_id = models.IntegerField()

    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                                 related_name='translation')

    value = models.CharField(max_length=255)

    def __str__(self):
        value_str = str(self.value)
        return f'{self.language.name}: {value_str[:10]}{"..." if len(value_str) > 10 else ""}'
