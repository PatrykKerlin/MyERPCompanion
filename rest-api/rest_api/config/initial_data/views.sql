INSERT INTO views (key, description, "order", controllers, module_id, is_active, created_at, created_by)
VALUES
('side_menu', 'Side menu view', 1, ARRAY['ModuleController'], 1, TRUE, NOW(), :superuser_id),
('current_user', 'Current user view', 1, ARRAY['CurrentUserController'], 1, TRUE, NOW(), :superuser_id),
('departments', 'Departments view', 3, ARRAY['DepartmentController'], 3, TRUE, NOW(), :superuser_id),
('positions', 'Positions view', 3, ARRAY['DepartmentController', 'PositionController'], 3, TRUE, NOW(), :superuser_id),
('employees', 'Employees view', 3, ARRAY['DepartmentController', 'PositionController', 'EmployeeController', 'UserController'], 3, TRUE, NOW(), :superuser_id);