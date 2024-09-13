from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .base_view import BaseView
from ..models import History
from ..serializers.history_serializers import *


class HistoryViews(BaseView):
    serializer_class = HistoryDetailSerializer
    queryset = History.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return HistoryListSerializer

        return self.serializer_class
