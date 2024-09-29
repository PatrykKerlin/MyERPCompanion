from django.db import models

from .image_model import Image
from .page_model import Page
from ..base.base_model import BaseModel
from ...managers.domain.page_images_manager import PageImagesManager


class PageImages(BaseModel):
    objects = PageImagesManager()

    class Meta:
        verbose_name = 'Page-Images'
        verbose_name_plural = 'Page-Images'
        db_table = 'core_page_images'
        unique_together = ('page', 'image')

    pageimages_id = models.IntegerField()

    page = models.ForeignKey(Page, on_delete=models.DO_NOTHING)
    image = models.ForeignKey(Image, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.image} - {self.page})'
