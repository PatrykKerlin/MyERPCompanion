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

    viewlabels_id = models.IntegerField()

    view = models.ForeignKey(View, on_delete=models.DO_NOTHING)
    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.view} - {self.label}'
