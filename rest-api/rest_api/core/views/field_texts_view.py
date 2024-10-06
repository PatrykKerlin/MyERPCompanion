from base.views.base_view import BaseView
from ..models import FieldTexts
from ..serializers.field_texts_serializer import FieldTextsSerializer


class FieldTextsView(BaseView):
    queryset = FieldTexts.objects.all()
    serializer_class = FieldTextsSerializer
