from django.db.models import TextChoices


class ThemesTextChoices(TextChoices):
    LIGHT = 'light', 'Light'
    DARK = 'dark', 'Dark'
