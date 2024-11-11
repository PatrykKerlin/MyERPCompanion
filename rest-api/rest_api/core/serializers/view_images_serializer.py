from base.serializers import BaseSerializer
from . import ViewSerializer, ImageSerializer
from ..models import ViewImages


class ViewImagesSerializer(BaseSerializer):
    view = ViewSerializer()
    image = ImageSerializer()

    class Meta:
        model = ViewImages

    @staticmethod
    def _get_list_fields():
        return ['view', 'image']
