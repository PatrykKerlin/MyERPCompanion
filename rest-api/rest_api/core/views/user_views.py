from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .base_view import BaseView
from ..models import User
from ..serializers.user_serializers import *


class UserViews(BaseView):
    serializer_class = UserListDetailSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer

        return self.serializer_class
