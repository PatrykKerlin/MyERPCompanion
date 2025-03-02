from django.db import models

from base.models import BaseModel
from .view_model import View
from .label_model import Label
from ..managers.generic_manager import GenericManager


class ViewLabels(BaseModel):
    objects = GenericManager()

    class Meta:
        verbose_name = 'View-Labels'
        verbose_name_plural = 'View-Labels'
        db_table = 'core_view_labels'
        unique_together = ('view', 'label')

    view = models.ForeignKey(View, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True})
    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True})

    def __str__(self):
        return f'{self.view} - {self.label}'
