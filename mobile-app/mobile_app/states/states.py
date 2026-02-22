from pydantic import Field
from schemas.core.user_schema import UserPlainSchema
from states.base.base_state import BaseState
from utils.translation import Translation


class TranslationState(BaseState):
    language: str
    items: Translation


class TokensState(BaseState):
    access: str | None = None
    refresh: str | None = None


class UserState(BaseState):
    current: UserPlainSchema | None = None


class MobileWarehouseState(BaseState):
    selected_id: int | None = None
    selected_name: str | None = None


class AppState(BaseState):
    translation: TranslationState
    tokens: TokensState
    user: UserState
    mobile_warehouse: MobileWarehouseState = Field(default_factory=MobileWarehouseState)
