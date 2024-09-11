from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings


class BaseModel(models.Model):
    class ModificationTypes(models.TextChoices):
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    modification_type = models.CharField(max_length=6, null=True, blank=True, choices=ModificationTypes.choices)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='%(class)s_modified')

    class Meta:
        abstract = True

    def save(self, user=None, initial=False, *args, **kwargs):
        instance_id_field_name = self.get_instance_id_field_name()

        if not user and initial:
            super().save(*args, **kwargs)
            return

        with transaction.atomic():
            if self._state.adding:
                if isinstance(self, get_user_model()):
                    self.created_by = user
                else:
                    last_instance_id_val = (self.__class__.objects
                                            .aggregate(models.Max(instance_id_field_name))[
                                                f'{instance_id_field_name}__max'] or 0)
                    setattr(self, instance_id_field_name, last_instance_id_val + 1)
                    self.created_by = user
            else:
                if isinstance(self, get_user_model()):
                    self.modified_by = user
                    self.modified_at = timezone.now()
                else:
                    original_entities = self.__class__.objects.filter(id=self.id, is_active=True)
                    self.id = None
                    original_instance_id_val = getattr(original_entities.first(), instance_id_field_name)
                    setattr(self, instance_id_field_name, original_instance_id_val)
                    original_entities.update(is_active=False,
                                             modified_by=user,
                                             modified_at=timezone.now(),
                                             modification_type=self.ModificationTypes.UPDATE)

        super().save(*args, **kwargs)

    def delete(self, user=None, *args, **kwargs):
        with transaction.atomic():
            self.is_active = False
            self.modification_type = self.ModificationTypes.DELETE
            self.modified_by = user
            self.modified_at = timezone.now()

            super().save(update_fields=['is_active', 'modified_by', 'modified_at', 'modification_type'])

    def get_instance_id_field_name(self):
        for field in self._meta.fields:
            if field.name.endswith('_id'):
                return field.name
        return None
