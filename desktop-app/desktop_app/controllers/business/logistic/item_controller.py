import asyncio
import mimetypes
import os
import subprocess
from typing import Any, cast

import flet as ft
from httpx import HTTPStatusError

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.core.image_schema import ImageStrictCreateSchema, ImageStrictUpdateSchema
from services.core.image_service import ImageService
from services.business.logistic import AssocBinItemService, BinService, CategoryService, ItemService, UnitService
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
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__bin_item_service = AssocBinItemService(self._settings, self._logger, self._tokens_accessor)

    def on_image_select_requested(self) -> None:
        self._page.run_task(self.__execute_pick_and_upload)

    def on_image_update_requested(self, image_id: int, new_order: int, is_primary: bool) -> None:
        self._page.run_task(self.__execute_image_update, image_id, new_order, is_primary)

    def on_image_delete_requested(self, image_id: int) -> None:
        self._page.run_task(self.__execute_image_delete, image_id)

    def on_table_row_clicked(self, result_id: int) -> None:
        self._page.run_task(
            self._execute_row_clicked,
            result_id,
            View.BINS,
            self.__bin_service,
            Endpoint.BINS,
        )

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ItemView:
        categories = await self.__perform_get_all_categories()
        units = await self.__perform_get_all_units()
        suppliers = await self.__perform_get_all_suppliers()
        currencies = await self.__perform_get_all_currencies()
        bins = await self.__perform_get_bins_for_item(event.data["id"]) if event.data else []
        return ItemView(
            self, translation, mode, event.view_key, event.data, categories, units, suppliers, currencies, bins
        )

    async def __perform_get_all_categories(self) -> list[tuple[int, str]]:
        schemas = await self.__category_service.get_all(Endpoint.CATEGORIES, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_units(self) -> list[tuple[int, str]]:
        schemas = await self.__unit_service.get_all(Endpoint.UNITS, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_suppliers(self) -> list[tuple[int, str]]:
        schemas = await self.__supplier_service.get_all(Endpoint.SUPPLIERS, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]

    async def __perform_get_bins_for_item(self, item_id: int) -> list[dict[str, Any]]:
        query_params = {"item_id": item_id}
        bin_item_schemas = await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS, None, query_params, None, self._module_id
        )
        if not bin_item_schemas:
            return []
        bin_ids = [schema.bin_id for schema in bin_item_schemas]
        body_params = {"ids": bin_ids}
        bins = await self.__bin_service.get_bulk(Endpoint.BINS_GET_BULK, None, None, body_params, self._module_id)
        quantity_by_bin_id = {schema.bin_id: schema.quantity for schema in bin_item_schemas}
        rows = []
        for bin_schema in bins:
            row = bin_schema.model_dump()
            row["quantity"] = quantity_by_bin_id.get(bin_schema.id, 0)
            rows.append(row)
        return rows

    async def __execute_pick_and_upload(self) -> None:
        file_path = await self.__pick_file_path()
        if not file_path:
            return
        await self.__perform_image_upload(file_path)

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

    async def __perform_image_upload(self, file_path: str) -> None:
        self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        if not self._view or not self._view.data_row:
            return
        item_id = self._view.data_row["id"]
        images = self._view.data_row["images"]
        is_primary = not self.__has_primary_image(images)
        max_order = max((image["order"] for image in images), default=0)
        next_order = max_order + 1
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
            body_params = {"data": form_data, "files": {"data": (file_name, data, content_type)}}
            response = await self.__image_service.create_multipart(
                Endpoint.IMAGES, None, None, body_params, self._module_id
            )
            images.append(response.model_dump())
            self._view.data_row["images"] = images
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

    async def __execute_image_update(self, image_id: int, new_order: int, is_primary: bool) -> None:
        if not self._view or not self._view.data_row:
            return
        images = self._view.data_row["images"]
        if not images:
            return
        ordered = sorted(images, key=lambda image: image["order"])
        current = next((image for image in ordered if image["id"] == image_id))
        max_order = len(ordered)
        normalized_order = max(1, min(new_order, max_order))
        reordered = [image for image in ordered if image["id"] != image_id]
        reordered.insert(normalized_order - 1, current)
        updates = []
        for index, image in enumerate(reordered, start=1):
            updated_primary = is_primary if image["id"] == image_id else image["is_primary"]
            if is_primary and image["id"] != image_id:
                updated_primary = False
            updates.append(
                ImageStrictUpdateSchema(
                    id=image["id"],
                    order=index,
                    is_primary=updated_primary,
                )
            )
        self._open_loading_dialog()
        try:
            await self.__execute_images_bulk_update(updates, primary_target_id=image_id if is_primary else None)
            self._close_loading_dialog()
        except Exception as error:
            self._close_loading_dialog()
            self._logger.error(str(error))
            self._open_error_dialog(message_key="cant_update_image")

    async def __execute_image_delete(self, image_id: int) -> None:
        if not self._view or not self._view.data_row:
            return
        confirm = await self._show_confirm_dialog("confirm_delete_image")
        if not confirm:
            return
        self._open_loading_dialog()
        try:
            images_before = self._view.data_row["images"]
            deleted_image = next((image for image in images_before if image["id"] == image_id), None)
            await self.__image_service.delete(Endpoint.IMAGES, image_id, None, None, self._module_id)
            images = [image for image in images_before if image["id"] != image_id]
            if images:
                ordered = sorted(images, key=lambda image: image["order"])
                updates = []
                for index, image in enumerate(ordered, start=1):
                    is_primary = image["is_primary"]
                    if deleted_image and deleted_image["is_primary"]:
                        is_primary = index == 1
                    updates.append(
                        ImageStrictUpdateSchema(
                            id=image["id"],
                            order=index,
                            is_primary=is_primary,
                        )
                    )
                await self.__execute_images_bulk_update(
                    updates,
                    primary_target_id=updates[0].id if deleted_image and deleted_image["is_primary"] else None,
                )
                images = self._view.data_row["images"]
            self._view.data_row["images"] = images
            self._view.set_images(images)
            self._close_loading_dialog()
        except HTTPStatusError as http_error:
            self._close_loading_dialog()
            if http_error.response.status_code == 403:
                self._open_error_dialog(message_key="no_permissions")
            else:
                self._logger.error(str(http_error))
                self._open_error_dialog(message_key="cant_delete_image")
        except Exception as error:
            self._close_loading_dialog()
            self._logger.error(str(error))
            self._open_error_dialog(message_key="cant_delete_image")

    async def __execute_images_bulk_update(
        self, updates: list[ImageStrictUpdateSchema], primary_target_id: int | None
    ) -> None:
        if not self._view or not self._view.data_row:
            return
        try:
            if primary_target_id is not None:
                cleared = [
                    ImageStrictUpdateSchema(id=update.id, order=update.order, is_primary=False) for update in updates
                ]
                body_params = cast(list[ImageStrictCreateSchema | ImageStrictUpdateSchema], cleared)
                await self.__image_service.update_bulk(
                    Endpoint.IMAGES_UPDATE_BULK, None, None, body_params, self._module_id
                )
            body_params = cast(list[ImageStrictCreateSchema | ImageStrictUpdateSchema], updates)
            response = await self.__image_service.update_bulk(
                Endpoint.IMAGES_UPDATE_BULK, None, None, body_params, self._module_id
            )
            updated_images = [item.model_dump() for item in response]
            self._view.data_row["images"] = updated_images
            self._view.set_images(updated_images)
        except HTTPStatusError as http_error:
            if http_error.response.status_code == 403:
                self._open_error_dialog(message_key="no_permissions")
            else:
                self._logger.error(str(http_error))
                self._open_error_dialog(message_key="cant_update_image")
        except Exception as error:
            self._logger.error(str(error))
            self._open_error_dialog(message_key="cant_update_image")
