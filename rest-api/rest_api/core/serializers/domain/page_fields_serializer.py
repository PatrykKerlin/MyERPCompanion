from rest_framework import serializers

from .page_serializer import PageSerializer
from .field_serializer import FieldSerializer
from ..base.base_serializer import BaseSerializer
from ...models import PageFields


class PageFieldsSerializer(BaseSerializer):
    page = serializers.SerializerMethodField()
    field = serializers.SerializerMethodField()

    class Meta:
        model = PageFields
        # fields = ['page_id', 'field_id']

    def get_fields(self):
        fields = super().get_fields()
        if self.context['view'].action != 'list':
            fields['page'] = PageSerializer()
            fields['field'] = FieldSerializer()

        return fields

    def get_page(self, obj):
        return obj.page.page_id

    def get_field(self, obj):
        return obj.field.field_id

    def _get_list_fields(self):
        return ['page', 'field']
