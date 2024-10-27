from django.db import models

from base.models.base_model import BaseModel
from base.fields_text_choices import FieldsTextChoices
from .label_model import Label
from ..managers.field_manager import FieldManager


class Field(BaseModel):
    objects = FieldManager()

    field_id = models.IntegerField()

    label = models.ForeignKey(Label, null=True, blank=True, on_delete=models.DO_NOTHING,
                              limit_choices_to={'is_active': True}, related_name='field')

    name = models.CharField(max_length=25)
    type = models.CharField(max_length=6, choices=FieldsTextChoices)
    required = models.BooleanField()

    def __str__(self):
        return self.name
