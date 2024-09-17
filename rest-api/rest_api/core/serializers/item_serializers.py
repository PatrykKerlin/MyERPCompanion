from .base_serializer import BaseSerializer
from ..models import Item
from ..helpers.model_fields import ModelFields


class ItemListSerializer(BaseSerializer):
    class Meta:
        model = Item
        fields = ['item_id', 'name', 'index']


class ItemCreateSerializer(ItemListSerializer):
    class Meta(ItemListSerializer.Meta):
        fields = ModelFields.get_model_specific_fields(ItemListSerializer.Meta.model)


class ItemDetailSerializer(ItemCreateSerializer):
    class Meta(ItemCreateSerializer.Meta):
        fields = (ItemCreateSerializer.Meta.fields +
                  ModelFields.get_model_common_fields(ItemCreateSerializer.Meta.model))
