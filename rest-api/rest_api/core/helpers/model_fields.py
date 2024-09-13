from ..models.base_model import BaseModel


class ModelFields:
    @staticmethod
    def get_model_common_fields():
        return BaseModel._BaseModel__get_model_common_fields()

    @staticmethod
    def get_model_specific_fields(Model):
        return [field.name for field in Model._meta.fields if field.name not in ModelFields.get_model_common_fields()]
