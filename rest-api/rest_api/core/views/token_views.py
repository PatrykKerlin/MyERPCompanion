from rest_framework.authtoken.views import ObtainAuthToken

from ..serializers.token_serializers import TokenSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = TokenSerializer
