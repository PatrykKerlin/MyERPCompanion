from __future__ import annotations

import flet as ft


class UserSettings:
    __WEB_THEME_KEY = "my_erp_companion.theme"
    __WEB_LANGUAGE_KEY = "my_erp_companion.language"

    @classmethod
    async def load_web(cls) -> tuple[str | None, str | None]:
        shared_preferences = ft.SharedPreferences()
        theme = await shared_preferences.get(cls.__WEB_THEME_KEY)
        language = await shared_preferences.get(cls.__WEB_LANGUAGE_KEY)
        return theme, language

    @classmethod
    async def save_web(cls, theme: str, language: str) -> None:
        shared_preferences = ft.SharedPreferences()
        await shared_preferences.set(cls.__WEB_THEME_KEY, theme)
        await shared_preferences.set(cls.__WEB_LANGUAGE_KEY, language)
