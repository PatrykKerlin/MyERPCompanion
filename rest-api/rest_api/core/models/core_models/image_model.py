from django.db import models

from .page_model import Page
from ..abstract_models.base_model import BaseModel
from ...managers.core_managers.image_manager import ImageManager


class Image(BaseModel):
    objects = ImageManager()

    image_id = models.IntegerField()

    # page = models.ForeignKey(Page, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
    #                          related_name='pages')
    key = models.CharField(max_length=50)
    value = models.ImageField(upload_to='pictures')

    def __str__(self):
        return f'{self.page.name}: {self.name}'
