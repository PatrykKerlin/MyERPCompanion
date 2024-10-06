from base.views.base_view import BaseView
from ..models import Text
from ..serializers.text_serializer import TextSerializer


class TextView(BaseView):
    queryset = Text.objects.all()
    serializer_class = TextSerializer