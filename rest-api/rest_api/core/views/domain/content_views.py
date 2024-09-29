from ..base.base_view import BaseView
from ...models import Text
from ...serializers.domain.content_serializers import ContentSerializer, ContentByPageSerializer


class ContentPrivateView(BaseView):
    queryset = Text.objects.all()
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
            return Text.objects.none()
        return Text.objects.by_page(page_id)
