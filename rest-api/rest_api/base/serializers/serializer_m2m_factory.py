from base.serializers import BaseSerializer


class SerializerM2MFactory:
    @staticmethod
    def get(Model, list_fields, field_serializers):
        class NewSerializer(BaseSerializer):
            class Meta:
                model = Model

            @staticmethod
            def _get_list_fields():
                return list_fields

        for field_name, serializer_class in field_serializers.items():
            setattr(NewSerializer, field_name, serializer_class())

        return NewSerializer
