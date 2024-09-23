from django.db import models

from .base_model import BaseModel
from ..managers.page_manager import PageManager


class Page(BaseModel):
    objects = PageManager()

    page_id = models.IntegerField(verbose_name="Page ID")

    name = models.CharField(max_length=50, unique=True, verbose_name="Page Name")
    title = models.CharField(max_length=50, verbose_name="Page Title")
    # description = models.TextField(null=True, blank=True, verbose_name="Page Description")
    # slug = models.CharField(max_length=255, unique=True, verbose_name="URL Path")
    template = models.CharField(max_length=50, verbose_name="Template Name",
                                help_text="HTML file name for rendering the page")
    # parent_page = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subpages',
    #                                 verbose_name="Parent Page")
    in_menu = models.BooleanField(default=True, verbose_name="Page visible in Menu")
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")

    def __str__(self):
        return self.title
