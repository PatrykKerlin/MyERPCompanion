from django.db.models import TextChoices


class FieldsTextChoices(TextChoices):
    TEXT = 'text', 'text'
    NUMBER = 'number', 'number'
    EMAIL = 'email', 'email'
    SELECT = 'select', 'select'
