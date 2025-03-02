from base.managers import BaseManager

from ..helpers import Defaults


class LabelManager(BaseManager):
    @staticmethod
    def get_translation_by_language(label, language=Defaults.LANGUAGE):
        translation = label.translations.filter(language__value=language).first()

        if not translation:
            translation = label.translations.filter(language__value=Defaults.LANGUAGE).first()

        return translation.value
