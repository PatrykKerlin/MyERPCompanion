from django.db import models

from base.models.base_model import BaseModel
from ..managers.image_manager import ImageManager


class Image(BaseModel):
    objects = ImageManager()

    image_id = models.IntegerField()

    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name
