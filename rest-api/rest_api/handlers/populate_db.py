from sqlalchemy import select
from sqlalchemy import func
from models.core import Group, User
from services.core import AuthService


class PopulateDB:
    def __init__(self, get_db):
        self.get_db = get_db

    async def __populate_groups(self) -> None:
        async with self.get_db() as db:
            result = await db.execute(select(func.count()).select_from(Group))
            count = result.scalar()
            if count == 0:
                admin_group = Group(
                    name="admins",
                    description="Administrators"
                )
                db.add(admin_group)
                await db.commit()
                await db.refresh(admin_group)

    async def __populate_admin(self) -> None:
        async with self.get_db() as db:
            result = await db.execute(select(func.count()).select_from(User))
            count = result.scalar()
            if count == 0:
                result_group = await db.execute(select(Group).filter(Group.name == "admins"))
                admin_group = result_group.scalars().first()
                hashed = AuthService.get_password_hash("admin")
                admin_user = User(username="admin", password=hashed, groups=[admin_group])
                db.add(admin_user)
                await db.commit()

    async def populate_db(self) -> None:
        await self.__populate_groups()
        await self.__populate_admin()
