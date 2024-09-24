from ..abstract_serializers.base_serializer import BaseSerializer
from ...models import Page


class PageSerializer(BaseSerializer):
    class Meta:
        model = Page

    def _get_list_fields(self):
        return '__all__'
