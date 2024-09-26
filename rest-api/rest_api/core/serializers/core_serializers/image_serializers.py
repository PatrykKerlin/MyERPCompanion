from ..abstract_serializers.base_serializer import BaseSerializer
from ...models import Image


class ImageSerializer(BaseSerializer):
    class Meta:
        model = Image

    def _get_list_fields(self):
        return ['page', 'key']


class ImageByPageSerializer(ImageSerializer):
    def _get_list_fields(self):
        return ['page', 'key', 'value']
