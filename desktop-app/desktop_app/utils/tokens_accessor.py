from typing import Any
from schemas.core.token_schema import TokenPlainSchema
from states.state_store import StateStore


class TokensAccessor:
    def __init__(self, state_store: StateStore) -> None:
        self.__state_store = state_store

    def read(self) -> TokenPlainSchema | None:
        tokens = self.__state_store.app_state.tokens
        return TokenPlainSchema(**tokens.model_dump()) if tokens else None

    def write(self, token: TokenPlainSchema) -> None:
        self.__state_store.update(tokens={**token.model_dump()})
