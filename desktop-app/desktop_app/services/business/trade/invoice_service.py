from __future__ import annotations

import re
from typing import Any

from schemas.business.trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class InvoiceService(BaseService[InvoicePlainSchema, InvoiceStrictSchema]):
    _plain_schema_cls = InvoicePlainSchema

    @BaseService.handle_token_refresh
    async def download_pdf(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: InvoiceStrictSchema | list[InvoiceStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> tuple[bytes, str | None]:
        if path_param is None:
            raise ValueError("Invoice ID is required for PDF download.")
        response = await self._get(
            endpoint=endpoint.format(invoice_id=path_param),
            query_params=query_params,
            tokens=tokens,
            module_id=module_id,
        )
        return response.content, self.__extract_filename(response.headers.get("content-disposition"))

    @staticmethod
    def __extract_filename(content_disposition: str | None) -> str | None:
        if not content_disposition:
            return None
        match = re.search(r'filename="?(?P<name>[^";]+)"?', content_disposition)
        if not match:
            return None
        filename = match.group("name").strip()
        return filename or None
