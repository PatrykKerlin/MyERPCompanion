from django.db import models

from base.models.base_model import BaseModel
from .text_model import Text
from ..managers.field_manager import FieldManager


class Field(BaseModel):
    objects = FieldManager()

    field_id = models.IntegerField()

    texts = models.ManyToManyField(Text, through='FieldTexts', limit_choices_to={'is_active': True},
                                   related_name='fields')

    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name
