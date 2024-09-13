from django.db import models, transaction
from django.apps import apps
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import json


class BaseModel(models.Model):
    version = models.IntegerField()
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='%(class)s_modified')

    class Meta:
        abstract = True

    @staticmethod
    def __get_history_model():
        return apps.get_model('core', 'History')

    @staticmethod
    def __datetime_json_serializer(instance):
        if isinstance(instance, datetime):
            return instance.isoformat()

    @staticmethod
    def __get_model_common_fields():
        return ['id'] + [field.name for field in BaseModel._meta.fields]

    def __create_new_history_record(self, History, prev_instance, modification_type):
        if not prev_instance.modified_by:
            created_by = self.created_by
        else:
            created_by = prev_instance.modified_by

        if not prev_instance.modified_at:
            created_at = self.created_at
        else:
            created_at = prev_instance.modified_at

        data = {field.name: getattr(prev_instance, field.name) for field in prev_instance._meta.fields if
                field.name not in ['password', "is_staff", "is_superuser"] + BaseModel.__get_model_common_fields()}
        data_json = json.dumps(data, default=self.__datetime_json_serializer)
        table_name = self._meta.app_label + '_' + self._meta.model_name.lower()

        history_record = History(
            table_name=table_name,
            record_id=self.id,
            version=prev_instance.version,
            modification_type=modification_type,
            data=data_json,
            created_by=created_by,
            created_at=created_at,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

        history_record.save()

    def save(self, *args, user=None, initial=False, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not user and initial:
            self.created_at = timezone.now()
            self.version = 1
        else:
            History = BaseModel.__get_history_model()
            with transaction.atomic():
                if not isinstance(self, History):
                    if self._state.adding:
                        self.created_at = timezone.now()
                        self.created_by = user
                        self.version = 1
                    else:
                        self.version += 1
                        self.modified_by = user
                        self.modified_at = timezone.now()
                        prev_instance = self.__class__.objects.get(pk=self.pk)
                        modification_type = History.ModificationTypes.UPDATE
                        self.__create_new_history_record(History, prev_instance, modification_type)

        super().save(*args, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    def delete(self, user=None, using=None, keep_parents=False):
        History = BaseModel.__get_history_model()
        if not isinstance(self, History):
            with transaction.atomic():
                self.modified_by = user
                self.modified_at = timezone.now()
                prev_instance = self.__class__.objects.get(pk=self.pk)
                modification_type = History.ModificationTypes.DELETE
                self.__create_new_history_record(History, prev_instance, modification_type)

        super().delete(using=using, keep_parents=keep_parents)
