from typing import Iterator

import flet as ft


class FieldGroup:
    def __init__(
        self,
        label: tuple[ft.Container, int],
        input: tuple[ft.Container, int],
        marker: tuple[ft.Container, int],
    ) -> None:
        self.__label = label[0]
        self.__input = input[0]
        self.__marker = marker[0]
        self.__columns = label[1] + input[1] + marker[1]

    def __iter__(self) -> Iterator[ft.Container]:
        yield from (self.label, self.input, self.marker)

    @property
    def label(self) -> ft.Container:
        return self.__label

    @property
    def input(self) -> ft.Container:
        return self.__input

    @property
    def marker(self) -> ft.Container:
        return self.__marker

    @property
    def columns(self) -> int:
        return self.__columns
