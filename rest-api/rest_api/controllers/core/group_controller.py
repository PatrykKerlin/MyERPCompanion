from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.core import GroupCreate, GroupOut
from services.core import GroupService


class GroupController:
    def __init__(self, get_db):
        self.get_db = get_db
        self.router = APIRouter()

        async def create_group_endpoint(
            group: GroupCreate, db: AsyncSession = Depends(self.get_db)
        ):
            return await GroupService.create_group(db, group.name)

        async def get_groups_endpoint(db: AsyncSession = Depends(self.get_db)):
            return await GroupService.get_all_groups(db)

        self.router.add_api_route(
            "/", create_group_endpoint, methods=["POST"], response_model=GroupOut
        )
        self.router.add_api_route(
            "/", get_groups_endpoint, methods=["GET"], response_model=list[GroupOut]
        )
