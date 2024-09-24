from ..abstract_serializers.base_serializer import BaseSerializer
from ...models import Content


class ContentSerializer(BaseSerializer):
    class Meta:
        model = Content

    def _get_list_fields(self):
        return ['page', 'name', 'lang']
