from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials!"
        )


class NoPermissionException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action!",
        )


class NotFoundException(HTTPException):
    def __init__(self, target: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{target} not found!",
        )


class SchemaAndDTOMissingException(ValueError):
    def __init__(self) -> None:
        super().__init__("Either schema or DTO must be provided!")


class DatabaseNotReadyException(Exception):
    def __init__(self) -> None:
        super().__init__("Database not ready after several retries!")
