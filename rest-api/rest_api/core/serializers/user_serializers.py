from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, IntegerField


class UserSerializer(ModelSerializer):
    user_id = IntegerField(source='id')

    class Meta:
        model = get_user_model()
        fields = ['user_id', 'username', 'password']
        read_only_fields = ['user_id']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
