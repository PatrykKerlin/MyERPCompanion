from django.contrib.admin import ModelAdmin

from ..helpers.model_fields import ModelFields


class BaseAdmin(ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        instance_id_field = ModelFields.get_instance_id_field_name(self.model)
        model_common_fields = ModelFields.get_model_common_fields(self.model)
        print('readonly')
        print([instance_id_field] + model_common_fields)
        return [instance_id_field] + model_common_fields

    def get_ordering(self, request, obj=None):
        return [ModelFields.get_instance_id_field_name(self.model)]

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [('Model fields', {'fields': ModelFields.get_model_specific_fields(self.model)}),
                     ('Additional information', {'fields': [ModelFields.get_instance_id_field_name(self.model)] +
                                                           ModelFields.get_model_common_fields(self.model)})]

        return fieldsets
