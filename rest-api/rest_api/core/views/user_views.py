from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .base_view import BaseView
from ..models import User
from ..serializers.user_serializer import UserSerializer


class UserView(BaseView):
    queryset = User.objects.all().order_by('id')
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
