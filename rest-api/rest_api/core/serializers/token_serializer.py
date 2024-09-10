from django.contrib.auth import authenticate
from rest_framework.serializers import Serializer, CharField, ValidationError


class UserTokenSerializer(Serializer):
    username = CharField()
    password = CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            message = 'Invalid Credentials'
            raise ValidationError(message, code='authentication')

        attrs['user'] = user
        return attrs
