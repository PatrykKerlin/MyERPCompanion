from rest_framework.response import Response
from rest_framework import status

from base.views.base_view import BaseView
from ..models import Page
from ..serializers.page_content_serializer import PageContentSerializer


class PageContentView(BaseView):
    serializer_class = PageContentSerializer

    def dispatch(self, request, *args, **kwargs):
        page_name = kwargs.get('page_name')

        if page_name == 'login':
            self.authentication_classes = []
            self.permission_classes = []

        return super().dispatch(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        page_name = kwargs.get('page_name', 'login')
        language = kwargs.get('language', 'en')

        page = Page.objects.get(name=page_name)

        serializer = self.serializer_class(page, context={'request': request, 'language': language})
        return Response(serializer.data, status=status.HTTP_200_OK)
