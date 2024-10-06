from base.views.base_view import BaseView
from ..models import PageFields
from ..serializers.page_fields_serializer import PageFieldsSerializer


class PageFieldsView(BaseView):
    queryset = PageFields.objects.all()
    serializer_class = PageFieldsSerializer
