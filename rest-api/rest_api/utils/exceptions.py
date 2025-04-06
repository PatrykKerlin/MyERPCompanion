from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials!") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class NoPermissionException(HTTPException):
    def __init__(
        self, detail: str = "You do not have permission to perform this action!"
    ) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found!") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ItemsNotFoundException(HTTPException):
    def __init__(self, item_type: str, missing_items: list[str]) -> None:
        message = f"Following {item_type} not found: {', '.join(missing_items)}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message
        )


class ConflictException(HTTPException):
    def __init__(
        self, detail: str = "Entity with the same unique field already exists!"
    ) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseNotReadyException(Exception):
    def __init__(
        self, message: str = "Database not ready after several retries!"
    ) -> None:
        super().__init__(message)
