from django.db import models

from .page_model import Page
from ..base.base_model import BaseModel
from ...managers.domain.content_manager import ContentManager


class Content(BaseModel):
    objects = ContentManager()

    content_id = models.IntegerField()

    page = models.ForeignKey(Page, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                             related_name='pages')
    key = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self):
        return f'{self.page.name}: {self.name}'
