from base.managers import BaseManager


class LabelManager(BaseManager):
    @staticmethod
    def get_translation_by_language(label, language='en'):
        translation = label.translations.filter(language__value=language).first()

        if not translation:
            translation = label.translations.filter(language__value='en').first()

        return translation.value
