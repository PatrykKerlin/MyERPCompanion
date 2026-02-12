from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from services.business.hr import EmployeeService, PositionService
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from utils.auth import Auth


class EmployeeController(BaseController[EmployeeService, EmployeeStrictSchema, EmployeePlainSchema]):
    _input_schema_cls = EmployeeStrictSchema
    _service_cls = EmployeeService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self.__position_service = PositionService()
        self._register_routes(EmployeePlainSchema)

    async def create(self, request: Request) -> EmployeePlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            position_id = body["position_id"]
            session = BaseController._get_request_session(request)
            position_schema = await self.__position_service.get_one_by_id(session, position_id)
            salary_range = (position_schema.min_salary, position_schema.max_salary)
            employee_schema = self._input_schema_cls.model_validate(body, context={"salary_range": salary_range})
            return await self._service.create(session, user.id, employee_schema)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.create.__qualname__}")
            raise
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.create.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.create.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def update(self, request: Request, model_id: int) -> EmployeePlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            position_id = body["position_id"]
            session = BaseController._get_request_session(request)
            position_schema = await self.__position_service.get_one_by_id(session, position_id)
            salary_range = (position_schema.min_salary, position_schema.max_salary)
            employee_schema = self._input_schema_cls.model_validate(body, context={"salary_range": salary_range})
            return await self._service.update(session, model_id, user.id, employee_schema)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.update.__qualname__}")
            raise
        except NoResultFound:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.update.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
            )
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.update.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.update.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
