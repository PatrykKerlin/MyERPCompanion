from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class BaseView(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)

    def get_serializer_class(self, serializers=None):
        if serializers and isinstance(serializers, dict):
            for action, serializer in serializers.items():
                if isinstance(action, str):
                    if self.action == action:
                        return serializer
                elif isinstance(action, list):
                    if self.action in action:
                        return serializer

        return super().get_serializer_class()
