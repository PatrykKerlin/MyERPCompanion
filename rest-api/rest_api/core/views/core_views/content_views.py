from ..abstract_views.base_view import BaseView
from ...models import Content
from ...serializers.core_serializers.content_serializer import ContentSerializer


class ContentPrivateView(BaseView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']


class ContentPublicView(ContentPrivateView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ['get']
