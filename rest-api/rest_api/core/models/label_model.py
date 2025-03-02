from django.db import models

from base.models import BaseModel
from ..managers.label_manager import LabelManager


class Label(BaseModel):
    objects = LabelManager()

    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name
