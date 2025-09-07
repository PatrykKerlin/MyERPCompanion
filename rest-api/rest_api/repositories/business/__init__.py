from models.business import AssocBinItem, Category, Department
from utils.factories import RepositoryFactory

from .hr.employee_repository import EmployeeRepository
from .hr.position_repository import PositionRepository
from .logistic.bin_repository import BinRepository
from .logistic.carrier_repository import CarrierRepository

DepartmentRepository = RepositoryFactory.create(Department)
AssocBinItemRepository = RepositoryFactory.create(AssocBinItem)
CategoryRepository = RepositoryFactory.create(Category)

__all__ = [
    "DepartmentRepository",
    "EmployeeRepository",
    "PositionRepository",
    "AssocBinItemRepository",
    "BinRepository",
    "CarrierRepository",
    "CategoryRepository",
]
