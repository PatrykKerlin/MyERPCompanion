from .base_view import BaseView
from ..models import User
from ..serializers.user_serializers import *


class UserViews(BaseView):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self, serializers=None):
        serializers = {
            ('list', 'retrieve'): UserListDetailSerializer,
            'create': UserCreateSerializer,
            ('update', 'partial_update'): UserUpdateSerializer,
        }

        return super().get_serializer_class(serializers=serializers)
