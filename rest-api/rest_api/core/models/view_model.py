from django.db import models

from base.models import BaseModel
from .module_model import Module
from .label_model import Label
from .image_model import Image
from ..managers.generic_manager import GenericManager


class View(BaseModel):
    objects = GenericManager()

    module = models.ForeignKey(Module, null=True, blank=True, on_delete=models.DO_NOTHING,
                               limit_choices_to={'is_active': True}, related_name='view')
    label = models.ForeignKey(Label, null=True, blank=True, on_delete=models.DO_NOTHING,
                              limit_choices_to={'is_active': True}, related_name='view')

    fields = models.ManyToManyField(Label, through='ViewLabels', limit_choices_to={'is_active': True},
                                    related_name='views')
    images = models.ManyToManyField(Image, through='ViewImages', limit_choices_to={'is_active': True},
                                    related_name='views')

    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=255)
    order = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
