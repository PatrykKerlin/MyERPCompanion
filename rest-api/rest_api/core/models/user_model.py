from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from base.models import BaseModel
from base.models.text_choices import Languages, Themes
from business.models.employee_model import Employee
from ..managers.user_manager import UserManager
from ..helpers import Defaults


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    employee = models.OneToOneField(Employee, null=True, blank=True, on_delete=models.DO_NOTHING,
                                    limit_choices_to={"is_active": True}, related_name="user")

    login = models.CharField(max_length=6, null=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    theme = models.CharField(max_length=5, choices=Themes.choices, default=Defaults.THEME.value)
    language = models.CharField(max_length=3, choices=Languages.choices, default=Defaults.LANGUAGE.value)

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ["password"]

    def __str__(self):
        return self.login

    def save(self, *args, user=None, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.login and self.employee:
            self.login = f"{self.employee.id:06d}"

        super().save(*args, user=user, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
