from ..base.base_serializer import BaseSerializer
from ...models import Text


class TextSerializer(BaseSerializer):
    class Meta:
        model = Text

    def _get_list_fields(self):
        return ['language', 'value']
