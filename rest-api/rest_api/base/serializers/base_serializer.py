from abc import abstractmethod

from rest_framework.fields import ModelField
from rest_framework.serializers import ModelSerializer, IntegerField
from collections import OrderedDict

from core.helpers.model_fields import ModelFields


class BaseSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        action = self.context.get('view', None) and getattr(self.context['view'], 'action', None)
        if action:
            self.Meta.fields = self.__get_fields_for_action(action)
        else:
            self.Meta.fields = self._get_detail_fields()

    def __get_fields_for_action(self, action):
        if action == 'list':
            fields = self._get_list_fields()
            if fields == '__all__':
                return self._get_detail_fields()
            return fields
        elif action == 'create':
            return self._get_create_fields()
        elif action in ['update', 'partial_update']:
            return self._get_update_fields()
        elif action == 'retrieve':
            return self._get_detail_fields()
        return []

    def _get_create_fields(self):
        return self._get_detail_fields()

    def _get_update_fields(self):
        return self._get_detail_fields()

    def _get_detail_fields(self):
        return (ModelFields.get_model_specific_fields(self.Meta.model) +
                ModelFields.get_model_common_fields(self.Meta.model))

    def get_fields(self):
        fields = super().get_fields()

        instance_id_field = ModelFields.get_instance_id_field_name(self.Meta.model)
        fields['id'] = IntegerField(source=instance_id_field, read_only=True)
        fields = OrderedDict([('id', fields['id'])] + [(key, value) for key, value in fields.items() if key != 'id'])

        common_fields = ModelFields.get_model_common_fields(self.Meta.model)
        for field_name in common_fields:
            if field_name in fields.keys():
                fields[field_name].read_only = True

        return fields

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

    @staticmethod
    @abstractmethod
    def _get_list_fields():
        pass
