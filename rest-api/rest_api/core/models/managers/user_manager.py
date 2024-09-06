from django.contrib.auth.models import BaseUserManager

from .base_manager import BaseManager


class UserManager(BaseManager, BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        username = username.strip()

        if not username:
            raise ValueError('User must have a username')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_superuser = True

        user.save(using=self._db)

        return user
