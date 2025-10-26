import asyncio
import os
import secrets
from pathlib import Path


class FileStorage:
    def __init__(self, root_dir: str, base_url: str, allowed_content: dict[str, str]) -> None:
        self.__root = Path(root_dir)
        self.__public_base_url = base_url.rstrip("/")
        self.__allowed_content = allowed_content

    def resolve_path(self, url: str) -> Path:
        prefix = self.__public_base_url.rstrip("/")
        relative_path = url[len(prefix) + 1 :]
        return self.__root / Path(relative_path)

    async def save_file(self, item_id: int, content_type: str, data: bytes) -> str:
        if content_type not in self.__allowed_content.keys():
            raise ValueError("Unsupported file content type")
        token = secrets.token_urlsafe(16)
        relative_dir = Path(str(item_id))
        relative_path = relative_dir / f"{token}.{self.__allowed_content[content_type]}"
        abs_path = self.__root / relative_path
        await asyncio.to_thread(abs_path.parent.mkdir, True, True)
        await asyncio.to_thread(abs_path.write_bytes, data)
        return f"{self.__public_base_url}/{relative_path.as_posix()}"

    async def delete_file(self, public_url: str) -> None:
        absolute_path = self.resolve_path(public_url)
        if absolute_path and absolute_path.exists():
            await asyncio.to_thread(os.remove, absolute_path)
