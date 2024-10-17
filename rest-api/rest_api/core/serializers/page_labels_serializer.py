from base.serializers.base_serializer import BaseSerializer
from .page_serializer import PageSerializer
from .label_serializer import LabelSerializer
from ..models import PageLabels


class PageLabelsSerializer(BaseSerializer):
    page = PageSerializer()
    label = LabelSerializer()

    class Meta:
        model = PageLabels

    def _get_list_fields(self):
        return ['page', 'label']
