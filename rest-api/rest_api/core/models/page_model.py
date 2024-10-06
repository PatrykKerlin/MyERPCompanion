from django.db import models

from base.models.base_model import BaseModel
from meta.models.category_model import Category
from .field_model import Field
from .image_model import Image

from ..managers.page_manager import PageManager


class Page(BaseModel):
    objects = PageManager()

    page_id = models.IntegerField()

    fields = models.ManyToManyField(Field, through='PageFields', limit_choices_to={'is_active': True},
                                    related_name='pages')
    images = models.ManyToManyField(Image, through='PageImages', limit_choices_to={'is_active': True},
                                    related_name='pages')

    category = models.ForeignKey(Category, null=True, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                                 related_name='pages')

    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=255)
    in_menu = models.BooleanField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.name
