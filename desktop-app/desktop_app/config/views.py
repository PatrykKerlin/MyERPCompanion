from dataclasses import dataclass, field


@dataclass
class Views:
    _views: dict[str, str] = field(
        default_factory=lambda: 
    )

    def get(self, key: str) -> str:
        return self._views[key]
