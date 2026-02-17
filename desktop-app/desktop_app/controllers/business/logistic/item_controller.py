import asyncio
import mimetypes
import os
import subprocess
from typing import Any, cast

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.trade.assoc_item_discount_schema import (
    AssocItemDiscountPlainSchema,
    AssocItemDiscountStrictSchema,
)
from schemas.business.trade.discount_schema import DiscountPlainSchema
from schemas.core.image_schema import ImageMultipartPayloadSchema, ImageStrictCreateSchema, ImageStrictUpdateSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import AssocBinItemService, BinService, CategoryService, ItemService, UnitService
from services.business.trade import AssocItemDiscountService, DiscountService, SupplierService
from services.core.image_service import ImageService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.item_view import ItemView

DiscountTransferItem = tuple[int, str, str, float | None]


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
        self.__discount_service = DiscountService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_item_discount_service = AssocItemDiscountService(
            self._settings, self._logger, self._tokens_accessor
        )
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

    def on_discount_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_discount_save)

    def on_discount_delete_clicked(self, discount_ids: list[int]) -> None:
        if not self._view or not discount_ids:
            return
        self._page.run_task(self.__handle_discount_delete, discount_ids)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ItemView:
        categories, units, suppliers = await asyncio.gather(
            self.__perform_get_all_categories(),
            self.__perform_get_all_units(),
            self.__perform_get_all_suppliers(),
        )
        if event.data:
            bins = await self.__perform_get_bins_for_item(event.data["id"])
        else:
            bins = []
        discount_source_items: list[DiscountTransferItem] = []
        discount_target_items: list[DiscountTransferItem] = []
        if mode != ViewMode.SEARCH:
            discount_target_items = await self.__extract_item_discounts(event.data)
            target_ids = {item[0] for item in discount_target_items}
            discount_source_items = await self.__perform_get_item_discount_options(target_ids)
        return ItemView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            categories,
            units,
            suppliers,
            bins,
            discount_source_items,
            discount_target_items,
            self.on_discount_save_clicked,
            self.on_discount_delete_clicked,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_categories(self) -> list[tuple[int, str]]:
        schemas = await self.__category_service.get_all(Endpoint.CATEGORIES, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_units(self) -> list[tuple[int, str]]:
        schemas = await self.__unit_service.get_all(Endpoint.UNITS, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_suppliers(self) -> list[tuple[int, str]]:
        schemas = await self.__supplier_service.get_all(Endpoint.SUPPLIERS, None, None, None, self._module_id)
        return [(schema.id, schema.company_name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_item_discount_options(self, exclude_ids: set[int]) -> list[DiscountTransferItem]:
        discounts = await self.__discount_service.get_all(Endpoint.DISCOUNTS, None, None, None, self._module_id)
        options: list[DiscountTransferItem] = []
        for discount in discounts:
            if not discount.for_items:
                continue
            if discount.id in exclude_ids:
                continue
            options.append((discount.id, discount.code, discount.name, discount.percent))
        return options

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_item_discounts(self, item_id: int) -> list[AssocItemDiscountPlainSchema]:
        return await self.__assoc_item_discount_service.get_all(
            Endpoint.ITEM_DISCOUNTS, None, {"item_id": item_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_discounts_by_ids(self, discount_ids: list[int]) -> list[DiscountPlainSchema]:
        if not discount_ids:
            return []
        body_params = IdsPayloadSchema(ids=discount_ids)
        return await self.__discount_service.get_bulk(
            Endpoint.DISCOUNTS_GET_BULK, None, None, body_params, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_bins_for_item(self, item_id: int) -> list[dict[str, Any]]:
        query_params = {"item_id": item_id}
        bin_item_schemas = await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS, None, query_params, None, self._module_id
        )
        if not bin_item_schemas:
            return []
        bin_ids = [schema.bin_id for schema in bin_item_schemas]
        body_params = IdsPayloadSchema(ids=bin_ids)
        bins = await self.__bin_service.get_bulk(Endpoint.BINS_GET_BULK, None, None, body_params, self._module_id)
        quantity_by_bin_id = {schema.bin_id: schema.quantity for schema in bin_item_schemas}
        rows = []
        for bin_schema in bins:
            row = bin_schema.model_dump()
            row["quantity"] = quantity_by_bin_id.get(bin_schema.id, 0)
            rows.append(row)
        return rows

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_item_discounts(self, payload: list[AssocItemDiscountStrictSchema]) -> None:
        await self._perform_create_bulk(
            self.__assoc_item_discount_service, Endpoint.ITEM_DISCOUNTS_CREATE_BULK, payload
        )

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_item_discounts(self, item_id: int, discount_ids: list[int]) -> None:
        assoc_rows = await self.__perform_get_item_discounts(item_id)
        assoc_ids = [row.id for row in assoc_rows if row.discount_id in discount_ids]
        if not assoc_ids:
            return
        body_params = IdsPayloadSchema(ids=assoc_ids)
        await self.__assoc_item_discount_service.delete_bulk(
            Endpoint.ITEM_DISCOUNTS_DELETE_BULK, None, None, body_params, self._module_id
        )

    async def __handle_discount_save(self) -> None:
        if not self._view or not self._view.data_row:
            return
        item_id = self._view.data_row["id"]
        pending_ids = self._view.get_pending_discount_ids()
        if not pending_ids:
            return
        payload = [
            AssocItemDiscountStrictSchema(item_id=item_id, discount_id=discount_id) for discount_id in pending_ids
        ]
        await self.__perform_create_item_discounts(payload)
        await self.__refresh_item_discount_lists(item_id)

    async def __handle_discount_delete(self, discount_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        item_id = self._view.data_row["id"]
        await self.__perform_delete_item_discounts(item_id, discount_ids)
        await self.__refresh_item_discount_lists(item_id)

    async def __extract_item_discounts(self, data: dict[str, Any] | None) -> list[DiscountTransferItem]:
        if not data:
            return []
        item_id = data.get("id")
        if not isinstance(item_id, int):
            return []
        assoc_rows = await self.__perform_get_item_discounts(item_id)
        discount_ids = [row.discount_id for row in assoc_rows]
        discounts = await self.__perform_get_discounts_by_ids(discount_ids)
        return [(discount.id, discount.code, discount.name, discount.percent) for discount in discounts]

    async def __refresh_item_discount_lists(self, item_id: int) -> None:
        if not self._view:
            return
        assoc_rows = await self.__perform_get_item_discounts(item_id)
        discount_ids = [row.discount_id for row in assoc_rows]
        discounts = await self.__perform_get_discounts_by_ids(discount_ids)
        target_items = [(discount.id, discount.code, discount.name, discount.percent) for discount in discounts]
        target_ids = {item[0] for item in target_items}
        source_items = await self.__perform_get_item_discount_options(target_ids)
        self._view.set_discount_target_items(target_items)
        self._view.set_discount_source_items(source_items)

    @BaseController.handle_api_action(ApiActionError.IMAGE_UPLOAD)
    async def __perform_image_upload(self, file_path: str) -> None:
        if not self._view or not self._view.data_row:
            return
        item_id = self._view.data_row["id"]
        images = self._view.data_row["images"]
        is_primary = not self.__has_primary_image(images)
        max_order = max((image["order"] for image in images), default=0)
        next_order = max_order + 1
        content_type = mimetypes.guess_type(file_path)[0] or "image/unknown"
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as file:
            data = file.read()
        form_data = {
            "is_primary": str(is_primary).lower(),
            "order": str(next_order),
            "content_type": content_type,
            "item_id": str(item_id),
        }
        body_params = ImageMultipartPayloadSchema(
            data=form_data,
            files={"data": (file_name, data, content_type)},
        )
        response = await self.__image_service.create_multipart(
            Endpoint.IMAGES, None, None, body_params, self._module_id
        )
        images.append(response.model_dump())
        self._view.data_row["images"] = images
        self._view.set_images(images)

    @BaseController.handle_api_action(ApiActionError.IMAGE_UPDATE)
    async def __perform_images_bulk_update(
        self, updates: list[ImageStrictUpdateSchema], primary_target_id: int | None
    ) -> None:
        if not self._view or not self._view.data_row:
            return
        if primary_target_id is not None:
            cleared = [
                ImageStrictUpdateSchema(id=update.id, order=update.order, is_primary=False) for update in updates
            ]
            body_params = cast(
                list[ImageStrictCreateSchema | ImageStrictUpdateSchema | ImageMultipartPayloadSchema], cleared
            )
            await self.__image_service.update_bulk(
                Endpoint.IMAGES_UPDATE_BULK, None, None, body_params, self._module_id
            )
        body_params = cast(
            list[ImageStrictCreateSchema | ImageStrictUpdateSchema | ImageMultipartPayloadSchema], updates
        )
        response = await self.__image_service.update_bulk(
            Endpoint.IMAGES_UPDATE_BULK, None, None, body_params, self._module_id
        )
        updated_images = [item.model_dump() for item in response]
        self._view.data_row["images"] = updated_images
        self._view.set_images(updated_images)

    @BaseController.handle_api_action(ApiActionError.IMAGE_DELETE)
    async def __perform_delete_image(self, image_id: int) -> None:
        await self.__image_service.delete(Endpoint.IMAGES, image_id, None, None, self._module_id)

    async def __execute_pick_and_upload(self) -> None:
        file_path = await self.__pick_file_path()
        if not file_path:
            return
        await self.__perform_image_upload(file_path)

    async def __pick_file_path(self) -> str | None:
        translation = self._state_store.app_state.translation.items
        try:
            return await asyncio.to_thread(self.__pick_linux_file)
        except Exception:
            self._logger.exception(f"Unhandled exception in {self.__pick_file_path.__qualname__}")
            self._open_error_dialog(message=translation.get("image_upload_unsupported"))
            return None

    def __pick_linux_file(self) -> str | None:
        translation = self._state_store.app_state.translation.items
        cwd = os.getcwd()
        env = os.environ.copy()
        env["WAYLAND_DISPLAY"] = env.get("WAYLAND_DISPLAY", "wayland-0")
        env["XDG_RUNTIME_DIR"] = env.get("XDG_RUNTIME_DIR", "/mnt/wslg/runtime-dir")
        env["XDG_SESSION_TYPE"] = "wayland"
        env["GDK_BACKEND"] = "wayland"
        args = [
            "zenity",
            "--file-selection",
            f"--title={translation.get('select_picture')}",
            f"--filename={cwd}/",
            "--file-filter=Images | *.png *.jpg *.jpeg",
        ]
        result = subprocess.run(args, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if stderr:
                self._logger.warning(f"Zenity file picker returned non-zero code with stderr: {stderr}")
            return None
        return result.stdout.strip() or None

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
        await self.__perform_images_bulk_update(updates, primary_target_id=image_id if is_primary else None)

    async def __execute_image_delete(self, image_id: int) -> None:
        if not self._view or not self._view.data_row:
            return
        confirm = await self._show_confirm_dialog("confirm_delete_image")
        if not confirm:
            return
        images_before = self._view.data_row["images"]
        deleted_image = next((image for image in images_before if image["id"] == image_id), None)
        await self.__perform_delete_image(image_id)
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
            await self.__perform_images_bulk_update(
                updates,
                primary_target_id=updates[0].id if deleted_image and deleted_image["is_primary"] else None,
            )
            images = self._view.data_row["images"]
        self._view.data_row["images"] = images
        self._view.set_images(images)
