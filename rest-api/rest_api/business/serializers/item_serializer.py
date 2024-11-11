from base.serializers import BaseSerializer
from ..models import Item


class ItemSerializer(BaseSerializer):
    class Meta:
        model = Item

    def _get_list_fields(self):
        return ['name', 'index']
