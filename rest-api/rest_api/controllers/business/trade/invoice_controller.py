from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import HTTPException, Request, Response, status
from schemas.business.trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
from services.business.trade import InvoiceService
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from utils.auth import Auth
from utils.enums import Permission


class InvoiceController(BaseController[InvoiceService, InvoiceStrictSchema, InvoicePlainSchema]):
    _input_schema_cls = InvoiceStrictSchema
    _service_cls = InvoiceService

    def __init__(self, context: Context, auth: Auth) -> None:
        BaseController.__init__(self, context, auth)
        self._service = InvoiceService(context.settings)
        self._register_routes(output_schema=InvoicePlainSchema)
        self.router.add_api_route(
            path="/{invoice_id:int}/pdf",
            endpoint=self.get_invoice_pdf,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )

    async def get_invoice_pdf(self, request: Request, invoice_id: int) -> Response:
        try:
            session = BaseController._get_request_session(request)
            content, filename = await self._service.build_invoice_pdf(session, invoice_id)
            headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
            return Response(content=content, media_type="application/pdf", headers=headers)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.get_invoice_pdf.__qualname__}")
            raise
        except NoResultFound:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.get_by_id.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=invoice_id),
            )
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.get_invoice_pdf.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
