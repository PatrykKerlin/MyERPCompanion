from collections.abc import Callable

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles, DialogStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class ItemDetailsDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        detail_rows: list[tuple[str, str]],
        image_urls: list[str],
        on_image_clicked: Callable[[str], None],
        on_ok_clicked: Callable[[ft.Event[ft.Button]], ft.DialogControl | None],
        safe_update: Callable[[ft.Control | None], None],
    ) -> None:
        self.__gallery_image_urls: list[str] = []
        self.__gallery_on_image_clicked: Callable[[str], None] | None = None
        self.__gallery_safe_update: Callable[[ft.Control | None], None] | None = None
        self.__gallery_start_index = 0
        self.__gallery_thumbnails_row: ft.Row | None = None
        self.__gallery_left_button: ft.IconButton | None = None
        self.__gallery_right_button: ft.IconButton | None = None

        details_rows: list[ft.Control] = [
            ft.Row(
                width=DialogStyles.ITEM_DETAILS_CONTENT_WIDTH,
                spacing=AppDimensions.SPACE_MD,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=DialogStyles.ITEM_DETAILS_LABEL_WIDTH,
                        alignment=ft.Alignment.TOP_LEFT,
                        content=self._get_label(translation.get(key), no_wrap=False),
                    ),
                    ft.Container(
                        width=DialogStyles.ITEM_DETAILS_VALUE_WIDTH,
                        alignment=ft.Alignment.TOP_LEFT,
                        content=self._get_label(value, no_wrap=False),
                    ),
                ],
            )
            for key, value in detail_rows
        ]
        controls: list[ft.Control] = [
            ft.Container(
                height=DialogStyles.ITEM_DETAILS_SCROLL_HEIGHT,
                content=ft.Column(
                    tight=True,
                    spacing=AppDimensions.SPACE_SM,
                    scroll=ft.ScrollMode.AUTO,
                    controls=details_rows,
                ),
            ),
            self.__build_gallery(
                image_urls=image_urls,
                on_image_clicked=on_image_clicked,
                safe_update=safe_update,
                translation=translation,
            ),
        ]
        super().__init__(
            title=translation.get("item_details"),
            controls=[
                ft.Container(
                    width=DialogStyles.ITEM_DETAILS_CONTENT_WIDTH,
                    content=ft.Column(controls=controls, tight=True, spacing=AppDimensions.SPACE_LG),
                )
            ],
            actions=[ft.Button(content=translation.get("ok"), on_click=on_ok_clicked, style=ButtonStyles.primary_regular)],
        )
        self.scrollable = False

    def __build_gallery(
        self,
        image_urls: list[str],
        on_image_clicked: Callable[[str], None],
        safe_update: Callable[[ft.Control | None], None],
        translation: Translation,
    ) -> ft.Control:
        if not image_urls:
            return ft.Container(
                content=self._get_label(translation.get("no_images")),
                padding=ft.Padding.all(AppDimensions.SPACE_SM),
            )

        self.__gallery_image_urls = list(image_urls)
        self.__gallery_on_image_clicked = on_image_clicked
        self.__gallery_safe_update = safe_update
        self.__gallery_start_index = 0
        self.__gallery_thumbnails_row = ft.Row(
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            expand=True,
        )
        self.__gallery_left_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            disabled=True,
            style=ButtonStyles.icon,
            on_click=self.__move_left,
        )
        self.__gallery_right_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            style=ButtonStyles.icon,
            on_click=self.__move_right,
        )
        self.__render_thumbnails()
        return ft.Container(
            width=DialogStyles.ITEM_DETAILS_CONTENT_WIDTH,
            content=ft.Row(
                width=DialogStyles.ITEM_DETAILS_CONTENT_WIDTH,
                controls=[self.__gallery_left_button, self.__gallery_thumbnails_row, self.__gallery_right_button],
                spacing=AppDimensions.SPACE_SM,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def __render_thumbnails(self) -> None:
        if self.__gallery_thumbnails_row is None:
            return
        self.__gallery_thumbnails_row.controls.clear()
        visible_count = DialogStyles.ITEM_DETAILS_GALLERY_VISIBLE_COUNT
        thumb_size = self.__resolve_gallery_thumb_size()
        for url in self.__gallery_image_urls[self.__gallery_start_index : self.__gallery_start_index + visible_count]:
            self.__gallery_thumbnails_row.controls.append(
                ft.Container(
                    expand=True,
                    height=thumb_size,
                    content=ft.Image(
                        src=url,
                        height=thumb_size,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    on_click=lambda _, selected_url=url: self.__on_image_clicked(selected_url),
                )
            )
        self.__safe_update(self.__gallery_thumbnails_row)
        self.__update_buttons()

    def __update_buttons(self) -> None:
        if self.__gallery_left_button is not None:
            self.__gallery_left_button.disabled = self.__gallery_start_index <= 0
            self.__safe_update(self.__gallery_left_button)
        if self.__gallery_right_button is not None:
            visible_count = DialogStyles.ITEM_DETAILS_GALLERY_VISIBLE_COUNT
            self.__gallery_right_button.disabled = self.__gallery_start_index + visible_count >= len(
                self.__gallery_image_urls
            )
            self.__safe_update(self.__gallery_right_button)

    def __move_left(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index <= 0:
            return
        self.__gallery_start_index -= 1
        self.__render_thumbnails()

    def __move_right(self, _: ft.Event[ft.IconButton]) -> None:
        visible_count = DialogStyles.ITEM_DETAILS_GALLERY_VISIBLE_COUNT
        if self.__gallery_start_index + visible_count >= len(self.__gallery_image_urls):
            return
        self.__gallery_start_index += 1
        self.__render_thumbnails()

    @staticmethod
    def __resolve_gallery_thumb_size() -> int:
        visible_count = DialogStyles.ITEM_DETAILS_GALLERY_VISIBLE_COUNT
        usable_width = (
            DialogStyles.ITEM_DETAILS_CONTENT_WIDTH
            - (2 * AppDimensions.ICON_BUTTON_WIDTH)
            - ((visible_count + 1) * AppDimensions.SPACE_SM)
        )
        return max(56, usable_width // visible_count)

    def __on_image_clicked(self, image_url: str) -> None:
        if self.__gallery_on_image_clicked is None:
            return
        self.__gallery_on_image_clicked(image_url)

    def __safe_update(self, control: ft.Control | None) -> None:
        if self.__gallery_safe_update is None:
            return
        self.__gallery_safe_update(control)
