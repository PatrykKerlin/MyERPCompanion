from base.serializers import BaseSerializer


class SerializerFactory:
    @staticmethod
    def get(Model, list_fields):
        class NewSerializer(BaseSerializer):
            class Meta:
                model = Model

            @staticmethod
            def _get_list_fields():
                return list_fields

        return NewSerializer
