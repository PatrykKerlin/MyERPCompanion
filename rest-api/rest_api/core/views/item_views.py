from .base_view import BaseView
from ..models import Item
from ..serializers.item_serializers import *


class ItemViews(BaseView):
    queryset = Item.objects.all()

    def get_serializer_class(self, serializers=None):
        serializers = {
            'list': ItemListSerializer,
            'retrieve': ItemDetailSerializer,
            ('create', 'update', 'partial_update'): ItemCreateSerializer,
        }

        return super().get_serializer_class(serializers=serializers)
