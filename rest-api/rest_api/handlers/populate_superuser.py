from getpass import getpass
from os import getenv

from sqlalchemy import func, select

from entities.core import User
from services.core import AuthService


class PopulateSuperuser:
    def __init__(self, get_db):
        self.__get_db = get_db

    async def populate_superuser(self) -> None:
        async with self.__get_db() as db:
            query = select(User).filter(
                User.is_active == True, User.is_superuser == True
            )
            result = await db.execute(query)
            existing_superuser = result.scalars().first()

            if existing_superuser:
                print("Superuser already exists.")
                return

            username = getenv("SUPERUSER_USERNAME", "")
            password = getenv("SUPERUSER_PASSWORD", "")
            hashed_password = AuthService.get_password_hash(password)
            superuser = User(
                username=username, password=hashed_password, is_superuser=True
            )
            db.add(superuser)
            await db.commit()
            print("Superuser created successfully.")
