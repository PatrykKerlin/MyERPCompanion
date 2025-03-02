from django.db.models import TextChoices


class Languages(TextChoices):
    ENG = "eng", "English"
    POL = "pol", "Polish"
