from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from base.models.base_model import BaseModel
from base.models.base_languages_model import BaseLanguagesModel
from business.models.employee_model import Employee
from ..managers.user_manager import UserManager


class User(BaseModel, BaseLanguagesModel, AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    class Themes(models.TextChoices):
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'dark'

    user_id = models.IntegerField()

    employee = models.ForeignKey(Employee, null=True, on_delete=models.DO_NOTHING, limit_choices_to={'is_active': True},
                                 related_name='employees')

    login = models.CharField(max_length=6, null=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    theme = models.CharField(max_length=5, choices=Themes.choices, default=Themes.DARK)
    language = models.CharField(max_length=2, choices=BaseLanguagesModel.Languages.choices,
                                default=BaseLanguagesModel.Languages.ENGLISH)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.login

    def save(self, *args, user=None, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.login and self.employee:
            self.login = f"{self.employee.id:06d}"

        if update_fields:
            if len(update_fields) == 1 and 'last_login' in update_fields:
                update_fields = None

        super().save(*args, user=user, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
