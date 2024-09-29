from ..base.base_view import BaseView
from ...models import Page
from ...serializers.domain.page_serializer import PageSerializer


class PageView(BaseView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
