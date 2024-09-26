from django.db import models

from ..base.base_model import BaseModel
from ...managers.domain.page_manager import PageManager


class Page(BaseModel):
    objects = PageManager()

    page_id = models.IntegerField()

    name = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=50)
    template = models.CharField(max_length=255)
    in_menu = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, unique=True)

    def __str__(self):
        return self.title
