from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from ..helpers.model_fields import ModelFields


class BaseView(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save(user=self.request.user)
        return instance

    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)

    def get_object(self):
        Model = self.get_queryset().model
        lookup_field = ModelFields.get_instance_id_field_name(Model)
        lookup_value = self.kwargs.get('pk')

        return self.get_queryset().get(**{lookup_field: lookup_value})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer)
        response_serializer = self.get_serializer(instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_update(serializer)
        response_serializer = self.get_serializer(instance)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
