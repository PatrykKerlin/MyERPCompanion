from django.contrib.auth.models import BaseUserManager

from base.managers.base_manager import BaseManager


class UserManager(BaseManager, BaseUserManager):
    def create_user(self, user=None, password=None, **extra_fields):
        new_user = self.model(**extra_fields)
        new_user.set_password(password)

        new_user.save(user=user)

        return new_user

    def create_superuser(self, **extra_fields):
        user = self.create_user(**extra_fields)

        self.model.objects.filter(id=user.id).update(
            is_staff=True,
            is_superuser=True,
            created_by=user
        )

        return user
