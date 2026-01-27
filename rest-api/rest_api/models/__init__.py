from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)  # type: ignore[name-defined]

shared_models = Path(__file__).resolve().parents[3] / "shared" / "models"
if shared_models.is_dir():
    __path__.append(str(shared_models))  # type: ignore[attr-defined]

__all__ = []
