from base.views.base_view import BaseView
from ..models import PageImages
from ..serializers.page_images_serializer import PageImagesSerializer


class PageImagesView(BaseView):
    queryset = PageImages.objects.all()
    serializer_class = PageImagesSerializer
