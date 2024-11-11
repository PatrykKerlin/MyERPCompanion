from django.contrib.auth import get_user_model

from base.views import BaseView
from ..serializers import UserSerializer


class UserView(BaseView):
    queryset = get_user_model().objects.all().order_by('id')
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = UserSerializer
