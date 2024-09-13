from .base_serializer import BaseSerializer
from ..models import History


class HistoryListSerializer(BaseSerializer):
    class Meta:
        model = History
        fields = ['id', 'table_name', 'record_id', 'modification_type', 'modified_at']


class HistoryDetailSerializer(HistoryListSerializer):
    class Meta(HistoryListSerializer.Meta):
        fields = (BaseSerializer.get_model_specific_fields(HistoryListSerializer.Meta.model) +
                  BaseSerializer.get_model_common_fields())
