from django.contrib.auth.models import BaseUserManager

from .base_manager import BaseManager


class UserManager(BaseManager, BaseUserManager):
    def create_user(self, user=None, password=None, initial=False, **extra_fields):
        new_user = self.model(**extra_fields)
        new_user.set_password(password)

        new_user.save(using=self._db, initial=initial, user=user)

        return new_user

    def create_superuser(self, initial=False, **extra_fields):
        user = self.create_user(initial=initial, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.created_by = user

        user.save(using=self._db, initial=initial, user=user)

        return user
