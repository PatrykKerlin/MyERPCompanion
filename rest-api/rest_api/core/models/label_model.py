from django.db import models

from base.models.base_model import BaseModel
from .translation_model import Translation
from ..managers.label_manager import LabelManager


class Label(BaseModel):
    objects = LabelManager()

    label_id = models.IntegerField()

    translations = models.ManyToManyField(Translation, through='LabelTranslations',
                                          limit_choices_to={'is_active': True},
                                          related_name='labels')

    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name
