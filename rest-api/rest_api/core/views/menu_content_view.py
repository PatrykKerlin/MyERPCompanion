from rest_framework.response import Response
from rest_framework import status

from base.views import BaseView
from ..models import Module
from ..serializers.menu_content_serializer import MenuContentSerializer


class MenuContentView(BaseView):
    serializer_class = MenuContentSerializer

    def list(self, request, *args, **kwargs):
        language = kwargs.get('language', 'en')

        modules = Module.objects.all()

        serializer = self.serializer_class(modules, many=True, context={'language': language})

        return Response(serializer.data, status=status.HTTP_200_OK)
