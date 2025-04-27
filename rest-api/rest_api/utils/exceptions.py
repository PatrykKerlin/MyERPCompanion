from typing import Any

from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials!") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class NoPermissionException(HTTPException):
    def __init__(self, detail: str = "You do not have permission to perform this action!") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found!") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ItemNotFoundException(HTTPException):
    def __init__(self, item_type: str, missing_item: Any) -> None:
        message = f"Following '{item_type}' not found: {missing_item}"
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)


class ValidationException(HTTPException):
    def __init__(self, item_type: str, detail: str) -> None:
        message = f"Validation error for '{item_type}': {detail}."
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Entity with the same unique field already exists!") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class SaveException(HTTPException):
    def __init__(self, detail: str = "Failed to save entity.") -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class DatabaseNotReadyException(Exception):
    def __init__(self, message: str = "Database not ready after several retries!") -> None:
        super().__init__(message)
