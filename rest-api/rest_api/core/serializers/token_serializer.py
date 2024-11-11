from django.contrib.auth import authenticate
from rest_framework.serializers import Serializer, CharField, ValidationError
from rest_framework.exceptions import APIException

from ..models.label_model import Label


class TokenSerializer(Serializer):
    login = CharField()
    password = CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            login=login,
            password=password
        )

        if not user:
            message = 'Invalid Credentials'
            raise ValidationError(message, code='authentication')

        attrs['user'] = user
        return attrs
