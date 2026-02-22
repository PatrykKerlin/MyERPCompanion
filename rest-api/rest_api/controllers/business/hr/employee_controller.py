from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Request
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from services.business.hr import EmployeeService, PositionService
from utils.auth import Auth


class EmployeeController(BaseController[EmployeeService, EmployeeStrictSchema, EmployeePlainSchema]):
    _input_schema_cls = EmployeeStrictSchema
    _service_cls = EmployeeService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self.__position_service = PositionService()
        self._register_routes(EmployeePlainSchema)

    @BaseController.handle_exceptions()
    async def create(self, request: Request) -> EmployeePlainSchema:
        user = request.state.user
        body = await request.json()
        position_id = body["position_id"]
        session = BaseController._get_request_session(request)
        position_schema = await self.__position_service.get_one_by_id(session, position_id)
        salary_range = (position_schema.min_salary, position_schema.max_salary)
        employee_schema = self._input_schema_cls.model_validate(body, context={"salary_range": salary_range})
        return await self._service.create(session, user.id, employee_schema)

    @BaseController.handle_exceptions()
    async def update(self, request: Request, model_id: int) -> EmployeePlainSchema:
        user = request.state.user
        body = await request.json()
        position_id = body["position_id"]
        session = BaseController._get_request_session(request)
        position_schema = await self.__position_service.get_one_by_id(session, position_id)
        salary_range = (position_schema.min_salary, position_schema.max_salary)
        employee_schema = self._input_schema_cls.model_validate(body, context={"salary_range": salary_range})
        return await self._service.update(session, model_id, user.id, employee_schema)
