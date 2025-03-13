import asyncio
from sqlalchemy.exc import OperationalError
from sqlalchemy.future import select
from models.core import User


class DBCheck:
    def __init__(self, get_db):
        self.get_db = get_db
        self.retries = 60
        self.delay = 1

    async def wait_for_db(self) -> None:
        for attempt in range(1, self.retries + 1):
            try:
                async with self.get_db() as db:
                    await db.execute(select(User).limit(1))
                    print("Database is ready.")
                return
            except OperationalError:
                print(f"Database not ready, attempt {attempt}/{self.retries}.")
                await asyncio.sleep(self.delay)
        raise Exception("Database not ready after several retries.")
