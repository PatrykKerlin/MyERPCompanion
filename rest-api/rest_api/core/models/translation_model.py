from django.db import models

from base.models import BaseModel
from base.models.text_choices import Languages
from . import Label
from ..managers.generic_manager import GenericManager


class Translation(BaseModel):
    objects = GenericManager()

    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING, limit_choices_to={"is_active": True},
                              related_name="translations")

    language = models.CharField(max_length=3, choices=Languages.choices)

    value = models.CharField(max_length=255)

    def __str__(self):
        value_str = str(self.value)
        lang_display = self.get_language_display()
        truncated_value = value_str if len(value_str) <= 25 else f"{value_str[:25]}..."
        return f"{lang_display}: {truncated_value}"
