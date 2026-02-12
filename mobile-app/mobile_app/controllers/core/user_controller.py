from __future__ import annotations

from typing import cast

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import MobileMainMenuRequested, TranslationRequested, ViewRequested
from pydantic import ValidationError
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateAppSchema
from schemas.validation.constraints import Constraints
from services.core import LanguageService, UserService
from utils.enums import ApiActionError, Endpoint, Module, View, ViewMode
from utils.translation import Translation
from views.core.user_view import UserView


class UserController(BaseViewController[UserService, UserView, UserPlainSchema, UserStrictUpdateAppSchema]):
    _plain_schema_cls = UserPlainSchema
    _strict_schema_cls = UserStrictUpdateAppSchema
    _service_cls = UserService
    _view_cls = UserView
    _view_key = View.USERS
    _endpoint = Endpoint.USERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self.__languages_by_id: dict[int, LanguagePlainSchema] = {}

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    def on_user_save_clicked(
        self,
        password: str | None,
        password_repeat: str | None,
        selected_language_id: int | None,
        selected_theme: Constraints.Theme,
    ) -> None:
        self._page.run_task(
            self.__handle_save_clicked,
            password,
            password_repeat,
            selected_language_id,
            selected_theme,
        )

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> UserView:
        user_schema = await self.__resolve_user_schema(event)
        if user_schema is None:
            user_schema = self._state_store.app_state.user.current
        if user_schema is None:
            return UserView(
                controller=self,
                translation=translation,
                mode=ViewMode.STATIC,
                view_key=event.view_key,
                data_row=event.data,
                languages=[],
                selected_language_id=0,
                selected_theme="system",
            )

        languages = await self.__perform_get_all_languages()
        language_pairs = self.__prepare_language_pairs(languages, user_schema.language)

        return UserView(
            controller=self,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=event.view_key,
            data_row=event.data,
            languages=language_pairs,
            selected_language_id=user_schema.language.id,
            selected_theme=self.__normalize_theme(user_schema.theme),
        )

    async def __handle_save_clicked(
        self,
        password: str | None,
        password_repeat: str | None,
        selected_language_id: int | None,
        selected_theme: Constraints.Theme,
    ) -> None:
        current_user = self._state_store.app_state.user.current
        if current_user is None:
            return
        if selected_language_id is None:
            self._open_error_dialog(message_key="value_required")
            return
        selected_language = self.__languages_by_id.get(selected_language_id)
        if selected_language is None:
            self._open_error_dialog(message_key="value_required")
            return

        normalized_password = self.__to_none_if_empty(password)
        normalized_password_repeat = self.__to_none_if_empty(password_repeat)

        try:
            payload = UserStrictUpdateAppSchema(
                id=current_user.id,
                username=current_user.username,
                password=normalized_password,
                password_repeat=normalized_password_repeat,
                language_id=selected_language_id,
                theme=selected_theme,
                employee_id=current_user.employee_id,
                customer_id=current_user.customer_id,
                warehouse_id=current_user.warehouse_id,
            )
        except ValidationError as validation_error:
            self.__handle_validation_error(validation_error)
            return

        updated_user = await self.__perform_update_user(current_user.id, payload)
        if updated_user is None:
            return

        effective_user = updated_user
        if effective_user.language.id != selected_language.id:
            effective_user = effective_user.model_copy(update={"language": selected_language})

        previous_language = self._state_store.app_state.translation.language
        self._state_store.update(user={"current": effective_user})
        if self._view:
            self._view.clear_password_inputs()
        self._open_message_dialog("record_save_success")
        await self._event_bus.publish(MobileMainMenuRequested())

        target_language = effective_user.language.symbol
        if target_language != previous_language:
            await self._event_bus.publish(TranslationRequested(target_language, True))

    async def __resolve_user_schema(self, event: ViewRequested) -> UserPlainSchema | None:
        if event.record_id is not None:
            return await self._perform_get_one(event.record_id, self._service, self._endpoint)
        return self._state_store.app_state.user.current

    def __prepare_language_pairs(
        self,
        languages: list[LanguagePlainSchema] | None,
        current_language: LanguagePlainSchema,
    ) -> list[tuple[int, str]]:
        pairs: list[tuple[int, str]] = []
        self.__languages_by_id = {}

        if languages:
            for language in languages:
                self.__languages_by_id[language.id] = language
                pairs.append((language.id, language.key))

        if current_language.id not in self.__languages_by_id:
            self.__languages_by_id[current_language.id] = current_language
            pairs.append((current_language.id, current_language.key))

        return sorted(pairs, key=lambda item: item[1].lower())

    def __handle_validation_error(self, validation_error: ValidationError) -> None:
        translation = self._state_store.app_state.translation.items
        error_message = [translation.get("validation_errors")]
        for error in validation_error.errors():
            message = error.get("msg", "")
            loc = error.get("loc", ())
            if loc:
                key = str(loc[0])
                error_message.append(f"{translation.get(key)}: {message}")
            else:
                error_message.append(message)
        self._open_error_dialog(message="\n".join(error_message))

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_languages(self) -> list[LanguagePlainSchema] | None:
        return await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, Module.CORE)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_user(
        self,
        user_id: int,
        payload: UserStrictUpdateAppSchema,
    ) -> UserPlainSchema | None:
        return await self._service.update(Endpoint.USERS, user_id, None, payload, Module.CORE)

    @staticmethod
    def __to_none_if_empty(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None

    @staticmethod
    def __normalize_theme(value: str | None) -> Constraints.Theme:
        if value in {"system", "dark", "light"}:
            return cast(Constraints.Theme, value)
        return "system"
