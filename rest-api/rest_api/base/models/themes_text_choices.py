from django.db.models import TextChoices


class Themes(TextChoices):
    LIGHT = 'light', 'Light'
    DARK = 'dark', 'Dark'
