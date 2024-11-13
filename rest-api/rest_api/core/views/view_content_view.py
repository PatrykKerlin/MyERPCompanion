from rest_framework.response import Response
from rest_framework import status

from base.views import BaseView
from ..models import View
from ..serializers.view_content_serializer import ViewContentSerializer


class ViewContentView(BaseView):
    serializer_class = ViewContentSerializer

    def dispatch(self, request, *args, **kwargs):
        view_name = kwargs.get('view_name')

        if view_name == 'login':
            self.authentication_classes = []
            self.permission_classes = []

        return super().dispatch(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        view_name = kwargs.get('view_name', '')
        language = kwargs.get('language', 'en')

        view = View.objects.get(name=view_name)

        serializer = self.serializer_class(view, context={'request': request, 'language': language})
        return Response(serializer.data, status=status.HTTP_200_OK)
