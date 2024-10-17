from django.db import models

from base.models.base_model import BaseModel
from .module_model import Module
from .label_model import Label
from .image_model import Image

from ..managers.page_manager import PageManager


class Page(BaseModel):
    objects = PageManager()

    page_id = models.IntegerField()

    module = models.ForeignKey(Module, null=True, blank=True, on_delete=models.DO_NOTHING,
                               limit_choices_to={'is_active': True}, related_name='pages')
    label = models.ForeignKey(Label, null=True, blank=True, on_delete=models.DO_NOTHING,
                              limit_choices_to={'is_active': True}, related_name='page_labels')

    labels = models.ManyToManyField(Label, through='PageLabels', limit_choices_to={'is_active': True},
                                    related_name='page_fields')
    images = models.ManyToManyField(Image, through='PageImages', limit_choices_to={'is_active': True},
                                    related_name='pages')

    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=255)
    order = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
