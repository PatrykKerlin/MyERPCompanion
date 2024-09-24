from ..abstract_views.base_view import BaseView
from ...models import Item
from ...serializers.business_serializers.item_serializer import ItemSerializer


class ItemView(BaseView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
