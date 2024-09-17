from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils import timezone

from ..serializers.token_serializers import TokenSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = TokenSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        user.last_login = timezone.now()
        user.save()

        return Response({'token': token.key})
