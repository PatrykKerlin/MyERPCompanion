from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers.user_manager import UserManager
from .base_model import BaseModel


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.username
