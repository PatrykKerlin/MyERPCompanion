from .base_serializer import BaseSerializer
from ..models import Item
from ..helpers.model_fields import ModelFields


class ItemSerializer(BaseSerializer):
    class Meta:
        model = Item

    def _get_list_fields(self):
        return ['name', 'index']
