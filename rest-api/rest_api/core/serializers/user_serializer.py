from django.contrib.auth import get_user_model
from rest_framework.serializers import IntegerField

from .base_serializer import BaseSerializer


class UserSerializer(BaseSerializer):
    class Meta:
        model = get_user_model()
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    def _get_list_fields(self):
        return ['employee', 'login']

    def create(self, validated_data, user=None):
        new_user = get_user_model().objects.create_user(user=user, **validated_data)
        return new_user

    def update(self, instance, validated_data, user=None):
        password = validated_data.pop('password', None)

        updated_user = super().update(instance, validated_data, user=user)

        if password:
            updated_user.set_password(password)

        updated_user.save(user=user)

        return updated_user
