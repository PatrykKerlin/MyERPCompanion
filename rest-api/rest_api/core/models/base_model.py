from django.db import models
from django.utils import timezone
from django.conf import settings

from ..middlewares.current_user_middleware import CurrentUserMiddleware


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='created_%(class)s_set')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='modified_%(class)s_set')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        initial = kwargs.pop('initial', False)
        user = kwargs.pop('user', None)

        if not user:
            user = CurrentUserMiddleware.get_current_user()

        if not user and initial:
            super().save(*args, **kwargs)
            return

        if self._state.adding and not self.created_by:
            self.created_by = user
        else:
            self.modified_by = user
            self.modified_at = timezone.now()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        self.is_active = False
        self.save(update_fields=['is_active', 'modified_by', 'modified_at'])
