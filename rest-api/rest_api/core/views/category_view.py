from base.views.base_view import BaseView
from ..models import Label
from ..serializers.label_serializer import LabelSerializer


class FieldView(BaseView):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
