from django.db import models

from base.models.base_model import BaseModel
from .field_model import Field
from .text_model import Text
from ..managers.field_texts_manager import FieldTextsManager


class FieldTexts(BaseModel):
    objects = FieldTextsManager()

    class Meta:
        verbose_name = 'Field-Texts'
        verbose_name_plural = 'Field-Texts'
        db_table = 'core_field_texts'
        unique_together = ('field', 'text')

    fieldtexts_id = models.IntegerField()

    field = models.ForeignKey(Field, on_delete=models.DO_NOTHING)
    text = models.ForeignKey(Text, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.field} - {self.text}'
