from __future__ import annotations

import json
from pathlib import Path


class UserSettings:
    @staticmethod
    def _path() -> Path:
        return Path.home() / ".config" / "my_erp_companion" / "user_prefs.json"

    @classmethod
    def load(cls) -> tuple[str | None, str | None]:
        path = cls._path()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, ValueError, TypeError):
            return None, None

        return payload.get("theme"), payload.get("language")

    @classmethod
    def save(cls, theme: str, language: str) -> None:
        path = cls._path()
        payload = {"theme": theme, "language": language}
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
            temp_path.replace(path)
        except OSError:
            return
