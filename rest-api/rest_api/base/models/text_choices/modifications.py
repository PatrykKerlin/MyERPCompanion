from django.db.models import TextChoices


class Modifications(TextChoices):
    INSERT = 'insert', 'Insert'
    UPDATE = 'update', 'Update'
    DELETE = 'delete', 'Delete'
