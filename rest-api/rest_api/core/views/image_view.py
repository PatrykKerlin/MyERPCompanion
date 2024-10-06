from base.views.base_view import BaseView
from ..models import Image
from ..serializers.image_serializer import ImageSerializer


class ImageView(BaseView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
