from django.db import models

from base.models.base_model import BaseModel
from .label_model import Label
from .translation_model import Translation
from ..managers.label_translations_manager import LabelTranslationsManager


class LabelTranslations(BaseModel):
    objects = LabelTranslationsManager()

    class Meta:
        verbose_name = 'Label-Translations'
        verbose_name_plural = 'Label-Translations'
        db_table = 'core_label_translations'
        unique_together = ('label', 'translation')

    labeltranslations_id = models.IntegerField()

    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING)
    translation = models.ForeignKey(Translation, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.label} - {self.translation}'
