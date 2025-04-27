from sqlalchemy.ext.asyncio import AsyncSession

from services.base import BaseService
from utils.exceptions import ItemNotFoundException, ValidationException


class SettingsValidator:
    @classmethod
    async def validate_key(
        cls,
        session: AsyncSession,
        service: BaseService,
        setting_id: int,
        expected_key: str,
    ) -> None:
        setting = await service.get_by_id(session, setting_id)
        if not setting:
            raise ItemNotFoundException(service._entity_cls.__name__, setting_id)
        if setting.key.key != expected_key:
            raise ValidationException(service._entity_cls.__name__, f"{setting.key.key} != {expected_key}")
