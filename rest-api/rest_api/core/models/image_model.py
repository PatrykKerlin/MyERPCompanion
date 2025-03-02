from django.db import models

from base.models import BaseModel
from ..managers.generic_manager import GenericManager


class Image(BaseModel):
    objects = GenericManager()

    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name
