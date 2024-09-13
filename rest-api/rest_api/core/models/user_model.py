from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from ..managers.user_manager import UserManager
from .base_model import BaseModel
from .employee_model import Employee


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    employee = models.OneToOneField(Employee, null=True, on_delete=models.CASCADE, related_name='user')
    login = models.CharField(max_length=6, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.login

    def save(self, *args, user=None, initial=False, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.login and self.employee:
            self.login = f"{self.employee.id:06d}"
        super().save(*args, user=user)
