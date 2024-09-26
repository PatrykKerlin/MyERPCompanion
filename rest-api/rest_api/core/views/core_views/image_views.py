from ..abstract_views.base_view import BaseView
from ...models import Image
from ...serializers.core_serializers.image_serializers import ImageSerializer, ImageByPageSerializer


class ImagePrivateView(BaseView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']


class ImagePublicView(ImagePrivateView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ['get']


class ImagePublicByPageView(ImagePublicView):
    serializer_class = ImageByPageSerializer

    def get_queryset(self):
        page_id = self.kwargs.get('id', None)
        if not page_id:
            return Image.objects.none()
        return Image.objects.by_page(page_id)
