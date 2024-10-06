from base.views.base_view import BaseView
from ..models import Page
from ..serializers.page_serializer import PageSerializer


class PageView(BaseView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
