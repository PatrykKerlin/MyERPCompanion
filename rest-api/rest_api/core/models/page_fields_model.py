from django.db import models

from base.models.base_model import BaseModel
from .page_model import Page
from .field_model import Field
from ..managers.page_fields_manager import PageFieldsManager


class PageFields(BaseModel):
    objects = PageFieldsManager()

    class Meta:
        verbose_name = 'Page-Fields'
        verbose_name_plural = 'Page-Fields'
        db_table = 'core_page_fields'
        unique_together = ('page', 'field')

    pagefields_id = models.IntegerField()

    page = models.ForeignKey(Page, on_delete=models.DO_NOTHING)
    field = models.ForeignKey(Field, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.page} - {self.field}'
