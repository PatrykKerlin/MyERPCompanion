from typing import TYPE_CHECKING
from config import Database
from sqlalchemy.orm import DeclarativeMeta

if TYPE_CHECKING:
    class _Base(DeclarativeMeta):
        pass
else:
    _Base = Database.get_base()

Base = _Base
