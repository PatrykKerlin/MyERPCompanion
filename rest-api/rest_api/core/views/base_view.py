from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..helpers.model_fields import ModelFields


class BaseView(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)

    # def get_serializer_class(self, serializers=None):
    #     if serializers and isinstance(serializers, dict):
    #         for action, serializer in serializers.items():
    #             if isinstance(action, str):
    #                 if self.action == action:
    #                     return serializer
    #             elif isinstance(action, list):
    #                 if self.action in action:
    #                     return serializer
    #
    #     return super().get_serializer_class()

    def get_object(self):
        Model = self.get_queryset().model
        lookup_field = ModelFields.get_instance_id_field_name(Model)
        lookup_value = self.kwargs.get('pk')

        return self.get_queryset().get(**{lookup_field: lookup_value})
