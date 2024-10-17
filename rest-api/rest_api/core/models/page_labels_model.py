from django.db import models

from base.models.base_model import BaseModel
from .page_model import Page
from .label_model import Label
from ..managers.page_labels_manager import PageLabelsManager


class PageLabels(BaseModel):
    objects = PageLabelsManager()

    class Meta:
        verbose_name = 'Page-Labels'
        verbose_name_plural = 'Page-Labels'
        db_table = 'core_page_labels'
        unique_together = ('page', 'label')

    pagelabels_id = models.IntegerField()

    page = models.ForeignKey(Page, on_delete=models.DO_NOTHING)
    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.page} - {self.label}'
