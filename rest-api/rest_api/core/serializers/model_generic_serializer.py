# from base.serializers.base_serializer import BaseSerializer
#
#
# class ModelGenericSerializer(BaseSerializer):
#     class Meta:
#         model = None
#
#     def __init__(self, model, list_fields):
#         super().__init__()
#         self.Meta.model = model
#         self.list_fields = list_fields
#
#     def _get_list_fields(self):
#         return self.list_fields
