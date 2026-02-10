from models.business.hr.department import Department
from models.business.hr.position import Position
from repositories.business.hr.employee_repository import EmployeeRepository
from utils.repository_factory import RepositoryFactory

DepartmentRepository = RepositoryFactory.create(Department)
PositionRepository = RepositoryFactory.create(Position)

__all__ = [
    "DepartmentRepository",
    "EmployeeRepository",
    "PositionRepository",
]
