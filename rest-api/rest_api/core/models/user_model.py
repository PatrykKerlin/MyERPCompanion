from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from ..managers.user_manager import UserManager
from .base_model import BaseModel
from .employee_model import Employee


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    user_id = models.IntegerField()
    employee = models.OneToOneField(Employee, null=True, on_delete=models.CASCADE, limit_choices_to={'is_active': True},
                                    related_name='employee')
    login = models.CharField(max_length=6, null=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

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
        print('user model')
        print(user)
        super().save(*args, user=user, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
