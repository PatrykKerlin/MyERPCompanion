from __future__ import annotations

from typing import TYPE_CHECKING, Any

from styles.styles import BaseViewStyles
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.translation_controller import TranslationController


class TranslationView(BaseView):
    def __init__(
        self,
        controller: TranslationController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        languages: list[tuple[int, str]],
    ) -> None:
        _ = languages
        super().__init__(
            controller=controller,
            translation=translation,
            mode=mode,
            view_key=key,
            data_row=data_row,
            base_label_size=BaseViewStyles.EMPTY_LABEL_SIZE,
            base_input_size=BaseViewStyles.EMPTY_INPUT_SIZE,
        )
