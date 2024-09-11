from rest_framework.viewsets import ModelViewSet


class BaseView(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)
