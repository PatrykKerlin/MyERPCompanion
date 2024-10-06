from django.db import models


class BaseLanguagesModel(models.Model):
    class Meta:
        abstract = True

    class Languages(models.TextChoices):
        ENGLISH = 'en', 'English'
        POLISH = 'pl', 'Polish'
