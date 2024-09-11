from rest_framework.serializers import ModelSerializer


class BaseSerializer(ModelSerializer):
    def create(self, validated_data, user=None):
        instance = self.Meta.model(**validated_data)
        instance.save(user=user)
        return instance

    def update(self, instance, validated_data, user=None):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(user=user)
        return instance
