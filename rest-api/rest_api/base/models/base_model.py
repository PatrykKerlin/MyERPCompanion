from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from core.helpers.model_fields import ModelFields

from .text_choices.modifications import Modifications


class BaseModel(models.Model):
    class Meta:
        abstract = True

    version = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)
    modification_type = models.CharField(max_length=6, null=True, blank=True, choices=Modifications.choices)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   limit_choices_to={'is_active': True}, related_name='%(class)s_created')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    limit_choices_to={'is_active': True}, related_name='%(class)s_modified')

    def save(self, *args, user=None, force_insert=False, force_update=False, using=None,
             update_fields=None):
        with transaction.atomic():
            if self._state.adding:
                self.created_by = user
                self.created_at = timezone.now()
                self.version = 1
                self.modification_type = Modifications.INSERT
            else:
                self.version += 1
                self.modification_type = Modifications.UPDATE
                self.modified_by = user
                self.modified_at = timezone.now()

            super().save(force_insert=force_insert, force_update=force_update, using=using,
                         update_fields=update_fields)

    def delete(self, user=None, using=None, keep_parents=False):
        self.version += 1
        self.is_active = False
        self.modification_type = Modifications.DELETE
        self.modified_by = user
        self.modified_at = timezone.now()

        super().save(update_fields=['version', 'is_active', 'modified_by', 'modified_at', 'modification_type'])
