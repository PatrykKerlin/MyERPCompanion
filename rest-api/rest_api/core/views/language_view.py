from base.views.base_view import BaseView
from ..models import Language
from ..serializers.language_serializer import LanguageSerializer


class LanguageView(BaseView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
