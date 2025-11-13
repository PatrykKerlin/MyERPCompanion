from __future__ import annotations

from collections.abc import Sequence
from typing import Callable

import flet as ft


class ImageGallery(ft.Row):
    def __init__(
        self,
        image_urls: Sequence[str] | None = None,
        *,
        image_width: float | None = 180,
        image_height: float | None = 120,
        image_fit: ft.ImageFit = ft.ImageFit.COVER,
        image_border_radius: float | ft.BorderRadius | None = 8,
        image_padding: float = 4,
        spacing: float = 12,
        expand: int | bool | None = None,
        on_image_click: Callable[[ft.ControlEvent, str], None] | None = None,
    ) -> None:
        super().__init__(
            spacing=spacing,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=expand,
        )
        self.image_width = image_width
        self.image_height = image_height
        self.image_fit = image_fit
        self.image_border_radius = image_border_radius
        self.image_padding = image_padding
        self.__on_image_click = on_image_click
        self.__image_urls = list(image_urls or [])
        self.controls = self.__build_images()

    # @property
    # def image_urls(self) -> list[str]:
    #     return list(self.__image_urls)

    # @image_urls.setter
    # def image_urls(self, urls: Sequence[str]) -> None:
    #     self.__image_urls = list(urls or [])
    #     self.controls = self.__build_images()
    #     self.update()

    # @property
    # def on_image_click(self) -> Callable[[ft.ControlEvent, str], None] | None:
    #     return self.__on_image_click

    # @on_image_click.setter
    # def on_image_click(self, callback: Callable[[ft.ControlEvent, str], None] | None) -> None:
    #     self.__on_image_click = callback
    #     if self.controls:
    #         self.controls = self.__build_images()
    #         self.update()

    # def add_image(self, url: str) -> None:
    #     self.__image_urls.append(url)
    #     self.controls = self.__build_images()
    #     self.update()

    # def clear_images(self) -> None:
    #     if not self.__image_urls:
    #         return
    #     self.__image_urls.clear()
    #     self.controls = []
    #     self.update()

    def __build_images(self) -> list[ft.Control]:
        containers: list[ft.Control] = []
        border_radius = self.__normalize_border_radius(self.image_border_radius)
        for url in self.__image_urls:
            image = ft.Image(
                src=url,
                width=self.image_width,
                height=self.image_height,
                fit=self.image_fit,
            )
            container = ft.Container(
                content=image,
                padding=self.image_padding,
                border_radius=border_radius,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                on_click=None if self.__on_image_click is None else self.__wrap_click(url),
            )
            containers.append(container)
        return containers

    def __wrap_click(self, url: str) -> Callable[[ft.ControlEvent], None]:
        def _handler(event: ft.ControlEvent) -> None:
            if self.__on_image_click is not None:
                self.__on_image_click(event, url)

        return _handler

    @staticmethod
    def __normalize_border_radius(
        border_radius: float | ft.BorderRadius | None,
    ) -> ft.BorderRadius | None:
        if border_radius is None:
            return None
        if isinstance(border_radius, ft.BorderRadius):
            return border_radius
        return ft.border_radius.all(border_radius)
