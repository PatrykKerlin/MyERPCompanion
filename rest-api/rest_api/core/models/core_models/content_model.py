from django.db import models

from .page_model import Page
from ..abstract_models.base_model import BaseModel
from ...managers.core_managers.content_manager import ContentManager


class Content(BaseModel):
    objects = ContentManager()

    content_id = models.IntegerField()

    page = models.ForeignKey(Page, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                             related_name='pages')
    name = models.CharField(max_length=50, unique=True)
    lang = models.CharField(max_length=2, default='en')
    value = models.TextField()

    def __str__(self):
        return f'{self.page.name}: {self.name}'
