from ..base.base_view import BaseView
from ...models import Page
from ...serializers.domain.page_serializer import PageSerializer


class PagePrivateView(BaseView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']


class PagePublicView(PagePrivateView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ['get']
