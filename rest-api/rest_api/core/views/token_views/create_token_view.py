from rest_framework.authtoken.views import ObtainAuthToken

from ...serializers.token_serializer import UserTokenSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = UserTokenSerializer
