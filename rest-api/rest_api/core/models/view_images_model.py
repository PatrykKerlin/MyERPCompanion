from django.db import models

from base.models import BaseModel
from .image_model import Image
from .view_model import View
from ..managers.generic_manager import GenericManager


class ViewImages(BaseModel):
    objects = GenericManager()

    class Meta:
        verbose_name = 'View-Images'
        verbose_name_plural = 'View-Images'
        db_table = 'core_view_images'
        unique_together = ('view', 'image')

    view = models.ForeignKey(View, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True})
    image = models.ForeignKey(Image, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True})

    def __str__(self):
        return f'{self.image} - {self.view})'
