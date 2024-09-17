from rest_framework.serializers import ModelSerializer

from ..models.base_model import BaseModel
from ..helpers.model_fields import ModelFields


class BaseSerializer(ModelSerializer):
    def save(self, **kwargs):
        user = kwargs.pop('user', None)
        validated_data = {**self.validated_data, **kwargs}

        if self.instance is None:
            return self.create(validated_data, user=user)
        else:
            return self.update(self.instance, validated_data, user=user)

    def create(self, validated_data, user=None):
        instance = self.Meta.model(**validated_data)
        instance.save(user=user)
        return instance

    def update(self, instance, validated_data, user=None):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(user=user)
        return instance
