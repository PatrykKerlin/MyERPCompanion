from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


class NotFoundException(HTTPException):
    def __init__(self, target: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{target} not found",
        )


class SchemaAndDTOMissingException(ValueError):
    def __init__(self):
        super().__init__("Either schema or DTO must be provided")


class DatabaseNotReadyException(Exception):
    def __init__(self):
        super().__init__("Database not ready after several retries.")
