from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from ..managers.user_manager import UserManager
from .base_model import BaseModel
from .employee_model import Employee


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    employee = models.OneToOneField(Employee, null=True, on_delete=models.CASCADE, related_name='user')
    username = models.CharField(max_length=5, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.username

    # def save(self, *args, **kwargs):
    #     if self.employee:
    #         self.username = f"{self.employee.primary_key:05}"
