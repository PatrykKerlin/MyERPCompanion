from ..base.base_view import BaseView
from ...models import Image
from ...serializers.domain.image_serializers import ImageSerializer


class ImagePrivateView(BaseView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']


class ImagePublicView(ImagePrivateView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ['get']
