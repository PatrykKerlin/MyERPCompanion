from django.db import models

from ..base.base_model import BaseModel
from ...managers.domain.image_manager import ImageManager


class Image(BaseModel):
    objects = ImageManager()

    image_id = models.IntegerField()

    name = models.CharField(max_length=50, unique=True)
    value = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name
