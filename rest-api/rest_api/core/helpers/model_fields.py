class ModelFields:
    @staticmethod
    def get_model_common_fields(Model):
        return [field.name for field in Model.__bases__[0]._meta.fields]

    @staticmethod
    def get_model_specific_fields(Model):
        return ([field.name for field in Model._meta.fields if
                 field.name not in ['id', 'is_superuser', 'is_staff', ModelFields.get_instance_id_field_name(Model)] +
                 ModelFields.get_model_common_fields(Model)])

    @staticmethod
    def get_instance_id_field_name(Model):
        return Model._meta.model_name + '_id'
