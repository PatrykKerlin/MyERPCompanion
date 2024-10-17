from base.serializers.base_serializer import BaseSerializer
from ..models import Module


class ModuleSerializer(BaseSerializer):
    class Meta:
        model = Module

    def _get_list_fields(self):
        return ['name']
