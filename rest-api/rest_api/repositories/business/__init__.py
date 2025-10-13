from models.business import AssocBinItem, Category, Department, Position, Currency
from utils.factories import RepositoryFactory

from .hr.employee_repository import EmployeeRepository
from .logistic.bin_repository import BinRepository
from .logistic.carrier_repository import CarrierRepository

DepartmentRepository = RepositoryFactory.create(Department)
PositionRepository = RepositoryFactory.create(Position)
AssocBinItemRepository = RepositoryFactory.create(AssocBinItem)
CategoryRepository = RepositoryFactory.create(Category)
CurrencyRepository = RepositoryFactory.create(Currency)

__all__ = [
    "DepartmentRepository",
    "EmployeeRepository",
    "PositionRepository",
    "AssocBinItemRepository",
    "BinRepository",
    "CarrierRepository",
    "CategoryRepository",
    "CurrencyRepository",
]
