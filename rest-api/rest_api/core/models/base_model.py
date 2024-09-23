from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from ..helpers.model_fields import ModelFields


class BaseModel(models.Model):
    class Meta:
        abstract = True

    class ModificationTypes(models.TextChoices):
        INSERT = 'insert', 'insert'
        UPDATE = 'update', 'update'
        DELETE = 'delete', 'delete'

    version = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)
    modification_type = models.CharField(max_length=6, null=True, blank=True, choices=ModificationTypes.choices)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='%(class)s_modified')

    def __add_historical_row(self):
        old_instance = self.__class__.objects.get(id=self.id)
        old_instance_fields = old_instance.__dict__.copy()
        old_instance_fields.pop('_state', None)
        old_instance_fields.pop('id')
        old_instance_fields['is_active'] = False

        if isinstance(self, get_user_model()):
            old_instance_fields['login'] = None

        self.__class__.objects.bulk_create([self.__class__(**old_instance_fields)])

    def save(self, *args, user=None, force_insert=False, force_update=False, using=None,
             update_fields=None):
        with transaction.atomic():
            instance_id_field_name = ModelFields.get_instance_id_field_name(self.__class__)
            if self._state.adding:
                last_instance_id_val = (self.__class__.objects
                                        .aggregate(models.Max(instance_id_field_name))[
                                            f'{instance_id_field_name}__max'] or 0)
                setattr(self, instance_id_field_name, last_instance_id_val + 1)
                self.created_by = user
                self.created_at = timezone.now()
                self.version = 1
                self.modification_type = BaseModel.ModificationTypes.INSERT
            else:
                self.__add_historical_row()

                self.version += 1
                self.modification_type = BaseModel.ModificationTypes.UPDATE
                self.modified_by = user
                self.modified_at = timezone.now()

            super().save(*args, force_insert=force_insert, force_update=force_update, using=using,
                         update_fields=update_fields)

    def delete(self, user=None, using=None, keep_parents=False):
        self.__add_historical_row()

        self.version += 1
        self.is_active = False
        self.modification_type = self.ModificationTypes.DELETE
        self.modified_by = user
        self.modified_at = timezone.now()

        super().save(update_fields=['version', 'is_active', 'modified_by', 'modified_at', 'modification_type'])
