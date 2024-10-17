from base.views.base_view import BaseView
from ..models import PageLabels
from ..serializers.page_labels_serializer import PageLabelsSerializer


class PageLabelsView(BaseView):
    queryset = PageLabels.objects.all()
    serializer_class = PageLabelsSerializer
