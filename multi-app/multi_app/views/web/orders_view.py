from __future__ import annotations

from typing import TYPE_CHECKING

from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.web.orders_controller import OrdersController


class OrdersView(BaseView["OrdersController"]):
    def __init__(self, controller: OrdersController, translation: Translation) -> None:
        super().__init__(
            controller=controller,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=View.WEB_ORDERS,
            data_row=None,
            base_label_size=0,
            base_input_size=0,
            base_columns_qty=12,
        )
