from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.business.hr.department_controller import DepartmentController
    from utils.translation import Translation


class DepartmentView(BaseView):
    def __init__(self, controller: DepartmentController, translation: Translation) -> None:
        super().__init__(controller, translation)
        fields = {
            "id": {
                "label": {
                    "content": ft.Text(value=f"{self._translation.get('id')}:"),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "input": {
                    "content": ft.TextField(value=""),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "marker": {
                    "content": self._get_field_marker("id"),
                    "col": 8,
                    "alignment": ft.alignment.center_left,
                },
            },
            "name": {
                "label": {
                    "content": ft.Text(value=f"{self._translation.get('name')}:"),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "input": {
                    "content": ft.TextField(value=""),
                    "col": 9,
                    "alignment": ft.alignment.center_left,
                },
                "marker": {
                    "content": self._get_field_marker("name"),
                    "col": 1,
                    "alignment": ft.alignment.center_left,
                },
            },
            "description": {
                "label": {
                    "content": ft.Text(value=f"{self._translation.get('description')}:"),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "input": {
                    "content": ft.TextField(value="", min_lines=5, max_lines=5),
                    "col": 9,
                    "alignment": ft.alignment.center_left,
                },
                "marker": {
                    "content": self._get_field_marker("description"),
                    "col": 1,
                    "alignment": ft.alignment.center_left,
                },
            },
            "code": {
                "label": {
                    "content": ft.Text(value=f"{self._translation.get('code')}:"),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "input": {
                    "content": ft.TextField(value=""),
                    "col": 9,
                    "alignment": ft.alignment.center_left,
                },
                "marker": {
                    "content": self._get_field_marker("code"),
                    "col": 1,
                    "alignment": ft.alignment.center_left,
                },
            },
            "email": {
                "label": {
                    "content": ft.Text(value=f"{self._translation.get('email')}:"),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "input": {
                    "content": ft.TextField(value=""),
                    "col": 9,
                    "alignment": ft.alignment.center_left,
                },
                "marker": {
                    "content": self._get_field_marker("email"),
                    "col": 1,
                    "alignment": ft.alignment.center_left,
                },
            },
            "phone_number": {
                "label": {
                    "content": ft.Text(value=f"{self._translation.get('phone')}:"),
                    "col": 2,
                    "alignment": ft.alignment.center_left,
                },
                "input": {
                    "content": ft.TextField(value=""),
                    "col": 9,
                    "alignment": ft.alignment.center_left,
                },
                "marker": {
                    "content": self._get_field_marker("phone_number"),
                    "col": 1,
                    "alignment": ft.alignment.center_left,
                },
            },
        }

        grid = self._build_grid(fields)
        self._master_column.controls.extend([grid])
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
