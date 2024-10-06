from django.db import models

from base.models.base_model import BaseModel
from ..managers.category_manager import CategoryManager


class Category(BaseModel):
    objects = CategoryManager()

    category_id = models.IntegerField()

    name = models.CharField(max_length=25)
    description = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
