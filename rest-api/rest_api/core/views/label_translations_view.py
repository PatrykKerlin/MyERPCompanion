from base.views.base_view import BaseView
from ..models import LabelTranslations
from ..serializers.label_translations_serializer import LabelTranslationsSerializer


class LabelTranslationsView(BaseView):
    queryset = LabelTranslations.objects.all()
    serializer_class = LabelTranslationsSerializer
