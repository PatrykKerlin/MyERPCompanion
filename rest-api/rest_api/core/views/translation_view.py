from base.views.base_view import BaseView
from ..models import Translation
from ..serializers.translation_serializer import TranslationSerializer


class TranslationView(BaseView):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
