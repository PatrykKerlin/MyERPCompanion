from .base_view import BaseView
from ..models import Item
from ..serializers.item_serializer import *


class ItemView(BaseView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
