from typing import Iterator

import flet as ft


class FieldGroup:
    def __init__(
        self,
        label: tuple[ft.Container, int] | None = None,
        input: tuple[ft.Container, int] | None = None,
        marker: tuple[ft.Container, int] | None = None,
    ) -> None:
        if input is None:
            raise ValueError("FieldGroup input is required.")
        self.__label = label[0] if label else None
        self.__input = input[0]
        self.__marker = marker[0] if marker else None
        self.__columns = (label[1] if label else 0) + input[1] + (marker[1] if marker else 0)

    @property
    def label(self) -> ft.Container | None:
        return self.__label

    @property
    def input(self) -> ft.Container:
        return self.__input

    @property
    def marker(self) -> ft.Container | None:
        return self.__marker

    @property
    def columns(self) -> int:
        return self.__columns

    def __iter__(self) -> Iterator[ft.Container]:
        if self.label is not None:
            yield self.label
        yield self.input
        if self.marker is not None:
            yield self.marker
