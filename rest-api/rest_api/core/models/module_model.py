from django.db import models

from base.models import BaseModel
from .label_model import Label
from ..managers.generic_manager import GenericManager


class Module(BaseModel):
    objects = GenericManager()

    module_id = models.IntegerField()

    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                              related_name='module')

    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name
