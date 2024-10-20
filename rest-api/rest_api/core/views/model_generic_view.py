# from base.views.base_view import BaseView
# from ..models import Image
# from ..serializers.model_generic_serializer import ModelGenericSerializer
#
#
# class ModelGenericView(BaseView):
#     serializer_class = ModelGenericSerializer
#
#     queryset = Image.objects.all()
#
#     def __init__(self, model, list_fields):
#         self.Model = model
#         self.list_fields = list_fields
#         self.queryset = self.Model.objects.all()
#
#     def get_serializer(self):
#         return self.serializer_class(self.Model, self.list_fields)
