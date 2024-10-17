from django.db import models

from base.models.base_model import BaseModel
from .label_model import Label
from ..managers.module_manager import ModuleManager


class Module(BaseModel):
    objects = ModuleManager()

    module_id = models.IntegerField()

    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                              related_name='modules')

    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name
