from django.contrib.admin import ModelAdmin


class BaseAdmin(ModelAdmin):
    readonly_fields = ['id', 'version', 'created_by', 'created_at', 'modified_by', 'modified_at']

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)
