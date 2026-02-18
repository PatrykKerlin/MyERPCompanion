from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Request, Response, status
from schemas.business.trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
from services.business.trade import InvoiceService
from utils.auth import Auth
from utils.enums import Permission


class InvoiceController(BaseController[InvoiceService, InvoiceStrictSchema, InvoicePlainSchema]):
    _input_schema_cls = InvoiceStrictSchema
    _service_cls = InvoiceService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._service = InvoiceService(context.settings)
        self._register_routes(output_schema=InvoicePlainSchema)
        self.router.add_api_route(
            path="/{invoice_id:int}/pdf",
            endpoint=self.get_invoice_pdf,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )

    @BaseController.handle_exceptions()
    async def get_invoice_pdf(self, request: Request, invoice_id: int) -> Response:
        session = BaseController._get_request_session(request)
        content, filename = await self._service.build_invoice_pdf(session, invoice_id)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return Response(content=content, media_type="application/pdf", headers=headers)
