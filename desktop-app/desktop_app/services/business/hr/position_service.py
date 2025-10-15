from schemas.business.hr.position_schema import PositionPlainSchema, PositionStrictSchema
from services.base.base_service import BaseService


class PositionService(BaseService[PositionPlainSchema, PositionStrictSchema]):
    _plain_schema_cls = PositionPlainSchema
