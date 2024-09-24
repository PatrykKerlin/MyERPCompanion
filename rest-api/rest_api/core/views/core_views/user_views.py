from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from ..abstract_views.base_view import BaseView
from ...serializers.core_serializers.user_serializer import UserSerializer


class UserView(BaseView):
    queryset = get_user_model().objects.all().order_by('id')
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = UserSerializer


class CurrentUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
