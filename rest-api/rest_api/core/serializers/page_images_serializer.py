from rest_framework import serializers

from base.serializers.base_serializer import BaseSerializer
from .page_serializer import PageSerializer
from .image_serializer import ImageSerializer
from ..models import PageImages


class PageImagesSerializer(BaseSerializer):
    page = PageSerializer()
    image = ImageSerializer()

    class Meta:
        model = PageImages

    def _get_list_fields(self):
        return ['page', 'image']
