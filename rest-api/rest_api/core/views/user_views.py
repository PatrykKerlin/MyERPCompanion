from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .base_view import BaseView
from ..models import User
from ..serializers.user_serializers import *


class UserViews(BaseView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
