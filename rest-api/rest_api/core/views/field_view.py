from base.views.base_view import BaseView
from ..models import Field
from ..serializers.field_serializer import FieldSerializer


class FieldView(BaseView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
