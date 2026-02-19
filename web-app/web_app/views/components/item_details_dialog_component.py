from collections.abc import Callable

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class ItemDetailsDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        detail_rows: list[tuple[str, str]],
        image_urls: list[str],
        on_image_clicked: Callable[[str], None],
        on_ok_clicked: Callable[[ft.Event[ft.TextButton]], ft.DialogControl | None],
        safe_update: Callable[[ft.Control | None], None],
    ) -> None:
        labels_column = ft.Column(
            controls=[ft.Text(translation.get(key)) for key, _ in detail_rows],
            tight=True,
        )
        values_column = ft.Column(
            controls=[ft.Text(value) for _, value in detail_rows],
            tight=True,
            expand=True,
        )
        controls: list[ft.Control] = [
            ft.Row(controls=[labels_column, values_column], spacing=AppDimensions.SPACE_XL, expand=True),
            self.__build_gallery(
                image_urls=image_urls,
                on_image_clicked=on_image_clicked,
                safe_update=safe_update,
                translation=translation,
            ),
        ]
        super().__init__(
            title=translation.get("item_details"),
            controls=controls,
            actions=[ft.TextButton(translation.get("ok"), on_click=on_ok_clicked, style=ButtonStyles.regular)],
        )

    @staticmethod
    def __build_gallery(
        image_urls: list[str],
        on_image_clicked: Callable[[str], None],
        safe_update: Callable[[ft.Control | None], None],
        translation: Translation,
    ) -> ft.Control:
        if not image_urls:
            return ft.Container(
                content=ft.Text(translation.get("no_images")),
                padding=ft.Padding.all(AppDimensions.SPACE_SM),
            )

        start_index = 0
        thumbnails_row = ft.Row(spacing=AppDimensions.SPACE_SM, run_spacing=AppDimensions.SPACE_SM)
        left_button = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, disabled=True, style=ButtonStyles.icon)
        right_button = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, style=ButtonStyles.icon)

        def update_buttons() -> None:
            left_button.disabled = start_index <= 0
            right_button.disabled = start_index + 3 >= len(image_urls)
            safe_update(left_button)
            safe_update(right_button)

        def render_thumbnails() -> None:
            thumbnails_row.controls.clear()
            for url in image_urls[start_index : start_index + 3]:
                thumbnails_row.controls.append(
                    ft.Container(
                        content=ft.Image(
                            src=url,
                            width=AppDimensions.DIALOG_THUMB_SIZE,
                            height=AppDimensions.DIALOG_THUMB_SIZE,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        on_click=lambda _, selected_url=url: on_image_clicked(selected_url),
                    )
                )
            safe_update(thumbnails_row)
            update_buttons()

        def move_left(_: ft.Event[ft.IconButton]) -> None:
            nonlocal start_index
            if start_index <= 0:
                return
            start_index -= 1
            render_thumbnails()

        def move_right(_: ft.Event[ft.IconButton]) -> None:
            nonlocal start_index
            if start_index + 3 >= len(image_urls):
                return
            start_index += 1
            render_thumbnails()

        left_button.on_click = move_left
        right_button.on_click = move_right
        render_thumbnails()
        return ft.Row(
            controls=[left_button, thumbnails_row, right_button],
            spacing=AppDimensions.SPACE_SM,
        )
