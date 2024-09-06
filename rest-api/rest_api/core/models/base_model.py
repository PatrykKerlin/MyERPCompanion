from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils import timezone

from ..middlewares.current_user_middleware import CurrentUserMiddleware


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('core.User', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='created_%(class)s_set')
    modified_by = models.ForeignKey('core.User', null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='modified_%(class)s_set')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = CurrentUserMiddleware.get_current_user()

        if user and not isinstance(user, AnonymousUser):
            if self._state.adding and not self.created_by:
                self.created_by = user
            else:
                self.modified_by = user

        if not self._state.adding:
            self.modified_at = timezone.now()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        self.is_active = False
        self.save(update_fields=['is_active', 'modified_by', 'modified_at'])
