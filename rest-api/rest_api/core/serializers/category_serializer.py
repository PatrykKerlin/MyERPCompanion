from base.serializers.base_serializer import BaseSerializer
from ..models import Category


class CategorySerializer(BaseSerializer):
    class Meta:
        model = Category

    def _get_list_fields(self):
        return ['name']
