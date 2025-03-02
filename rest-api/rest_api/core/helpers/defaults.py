from enum import Enum

from base.models.text_choices import Languages, Themes


class Defaults(Enum):
    LANGUAGE = Languages.ENG
    THEME = Themes.DARK
