from base.serializers.base_serializer import BaseSerializer
from .page_serializer import PageSerializer
from .field_serializer import FieldSerializer
from ..models import PageFields


class PageFieldsSerializer(BaseSerializer):
    page = PageSerializer()
    field = FieldSerializer()

    class Meta:
        model = PageFields

    def _get_list_fields(self):
        return ['page', 'field']
