from rest_framework.generics import CreateAPIView

from ...serializers.user_serializer import UserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
