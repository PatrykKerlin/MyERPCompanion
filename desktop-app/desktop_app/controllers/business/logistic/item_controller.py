import asyncio
import mimetypes
import os
import subprocess
from typing import Any

import flet as ft

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from services.core.image_service import ImageService
from services.business.logistic import CategoryService, ItemService, UnitService
from services.business.trade import CurrencyService, SupplierService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.item_view import ItemView
from events.events import ViewRequested


class ItemController(BaseViewController[ItemService, ItemView, ItemPlainSchema, ItemStrictSchema]):
    _plain_schema_cls = ItemPlainSchema
    _strict_schema_cls = ItemStrictSchema
    _service_cls = ItemService
    _view_cls = ItemView
    _endpoint = Endpoint.ITEMS
    _view_key = View.ITEMS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__category_service = CategoryService(self._settings, self._logger, self._tokens_accessor)
        self.__unit_service = UnitService(self._settings, self._logger, self._tokens_accessor)
        self.__supplier_service = SupplierService(self._settings, self._logger, self._tokens_accessor)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__image_service = ImageService(self._settings, self._logger, self._tokens_accessor)

    def on_image_select_requested(self) -> None:
        self._page.run_task(self.__execute_pick_and_upload)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ItemView:
        categories = await self.__perform_get_all_categories()
        units = await self.__perform_get_all_units()
        suppliers = await self.__perform_get_all_suppliers()
        currencies = await self.__perform_get_all_currencies()
        return ItemView(self, translation, mode, event.view_key, event.data, categories, units, suppliers, currencies)

    async def __perform_get_all_categories(self) -> list[tuple[int, str]]:
        schemas = await self.__category_service.call_api_with_token_refresh(
            func=self.__category_service.get_all,
            endpoint=Endpoint.CATEGORIES,
            module_id=self._module_id,
        )
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_units(self) -> list[tuple[int, str]]:
        schemas = await self.__unit_service.call_api_with_token_refresh(
            func=self.__unit_service.get_all,
            endpoint=Endpoint.UNITS,
            module_id=self._module_id,
        )
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_suppliers(self) -> list[tuple[int, str]]:
        schemas = await self.__supplier_service.call_api_with_token_refresh(
            func=self.__supplier_service.get_all,
            endpoint=Endpoint.SUPPLIERS,
            module_id=self._module_id,
        )
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.call_api_with_token_refresh(
            func=self.__currency_service.get_all,
            endpoint=Endpoint.CURRENCIES,
            module_id=self._module_id,
        )
        return [(schema.id, schema.code) for schema in schemas]

    async def __execute_pick_and_upload(self) -> None:
        file_path = await self.__pick_file_path()
        if not file_path:
            return
        await self.__execute_image_upload(file_path)

    async def __pick_file_path(self) -> str | None:
        platform = self._page.platform
        translation = self._state_store.app_state.translation.items
        try:
            if platform == ft.PagePlatform.WINDOWS:
                return await asyncio.to_thread(self.__pick_windows_file)
            if platform == ft.PagePlatform.LINUX:
                return await asyncio.to_thread(self.__pick_linux_file)
            self._open_error_dialog(message=translation.get("image_upload_not_supported"))
            return None
        except Exception as error:
            self._logger.error(str(error))
            self._open_error_dialog(message=translation.get("image_upload_not_supported"))
            return None

    def __pick_linux_file(self) -> str | None:
        translation = self._state_store.app_state.translation.items
        cwd = os.getcwd()
        args = [
            "zenity",
            "--file-selection",
            f"--title={translation.get("select_picture")}",
            f"--filename={cwd}/",
            "--file-filter=Images | *.png *.jpg *.jpeg",
        ]
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def __pick_windows_file(self) -> str | None:
        cwd = os.getcwd()
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$f = New-Object System.Windows.Forms.OpenFileDialog; "
            "$f.Multiselect = $false; "
            f"$f.InitialDirectory = '{cwd}'; "
            "$f.Filter = "
            "'Images (*.png;*.jpg;*.jpeg)|*.png;*.jpg;*.jpeg'; "
            "if($f.ShowDialog() -eq 'OK'){ Write-Output $f.FileName }"
        )
        result = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    async def __execute_image_upload(self, file_path: str) -> None:
        self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        if not self._view or not self._view.data_row:
            return
        item_id = self._view.data_row["id"]
        images = self._view.data_row["images"]

        max_order = max((image["order"] for image in images), default=0)
        next_order = max_order + 1
        is_primary = not self.__has_primary_image(images)

        content_type = mimetypes.guess_type(file_path)[0]
        file_name = os.path.basename(file_path)

        try:
            with open(file_path, "rb") as file:
                data = file.read()
        except Exception as error:
            self._open_loading_dialog()
            self._logger.error(str(error))
            self._open_error_dialog(message=translation.get("cant_read_file"))
            return

        try:
            form_data = {
                "is_primary": str(is_primary).lower(),
                "order": str(next_order),
                "content_type": content_type,
                "item_id": str(item_id),
            }
            response = await self.__image_service.call_api_with_token_refresh(
                func=self.__image_service.create_multipart,
                endpoint=Endpoint.IMAGES,
                body_params={
                    "data": form_data,
                    "files": {"data": (file_name, data, content_type)},
                },
                module_id=self._module_id,
            )
            if not isinstance(images, list):
                images = []
                self._view.data_row["images"] = images
            images.append(response.model_dump())
            self._view.set_images(images)
            self._close_loading_dialog()
        except Exception as error:
            self._close_loading_dialog()
            self._logger.error(str(error))
            self._open_error_dialog(message=translation.get("cant_upload_file"))

    def __has_primary_image(self, images: list[dict[str, Any]]) -> bool:
        for image in images:
            if image["is_primary"]:
                return True
        return False
