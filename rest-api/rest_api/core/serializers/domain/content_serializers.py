from ..base.base_serializer import BaseSerializer
from ...models import Text


class ContentSerializer(BaseSerializer):
    class Meta:
        model = Text

    def _get_list_fields(self):
        return ['page', 'key']


class ContentByPageSerializer(ContentSerializer):
    def _get_list_fields(self):
        return ['page', 'key', 'value']
