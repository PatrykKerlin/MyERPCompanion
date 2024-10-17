from base.views.base_view import BaseView
from ..models import Module
from ..serializers.module_serializer import ModuleSerializer


class ModuleView(BaseView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
