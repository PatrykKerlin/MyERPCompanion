INSERT INTO views (key, description, "order", controllers, module_id, is_active, created_at, created_by)
VALUES
('side_menu', 'Side menu view', 1, ARRAY['ModuleController'], 1, TRUE, NOW(), :superuser_id),
('current_user', 'Current user view', 1, ARRAY['CurrentUserController'], 1, TRUE, NOW(), :superuser_id),
('departments', 'Departments view', 1, ARRAY['DepartmentController'], 3, TRUE, NOW(), :superuser_id),
('positions', 'Positions view', 2, ARRAY['DepartmentController', 'PositionController', 'CurrencyController'], 3, TRUE, NOW(), :superuser_id),
('employees', 'Employees view', 3, ARRAY['DepartmentController', 'PositionController', 'EmployeeController'], 3, TRUE, NOW(), :superuser_id),
('warehouses', 'Warehouses view', 1, ARRAY['WarehouseController'], 4, TRUE, NOW(), :superuser_id),
('bins', 'Bins view', 2, ARRAY['BinController', 'WarehouseController'], 4, TRUE, NOW(), :superuser_id);