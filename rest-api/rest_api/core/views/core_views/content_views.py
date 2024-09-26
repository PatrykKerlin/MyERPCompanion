from ..abstract_views.base_view import BaseView
from ...models import Content
from ...serializers.core_serializers.content_serializers import ContentSerializer, ContentByPageSerializer


class ContentPrivateView(BaseView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']


class ContentPublicView(ContentPrivateView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ['get']


class ContentPublicByPageView(ContentPublicView):
    serializer_class = ContentByPageSerializer

    def get_queryset(self):
        page_id = self.kwargs.get('id', None)
        if not page_id:
            return Content.objects.none()
        return Content.objects.by_page(page_id)
