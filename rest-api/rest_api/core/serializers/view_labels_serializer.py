from base.serializers import BaseSerializer
from . import ViewSerializer, LabelSerializer
from ..models import ViewLabels


class ViewLabelsSerializer(BaseSerializer):
    view = ViewSerializer()
    label = LabelSerializer()

    class Meta:
        model = ViewLabels

    @staticmethod
    def _get_list_fields():
        return ['view', 'label']
