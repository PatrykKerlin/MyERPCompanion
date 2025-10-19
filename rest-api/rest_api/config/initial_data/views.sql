INSERT INTO views (key, description, "order", module_id, is_active, created_at, created_by)
VALUES
('side_menu', 'Side menu view', 1, 1, TRUE, NOW(), :superuser_id),
('current_user', 'Current user view', 2, 1, TRUE, NOW(), :superuser_id),
('departments', 'Departments view', 1, 3, TRUE, NOW(), :superuser_id),
('positions', 'Positions view', 2, 3, TRUE, NOW(), :superuser_id),
('employees', 'Employees view', 3, 3, TRUE, NOW(), :superuser_id),
('warehouses', 'Warehouses view', 1, 4, TRUE, NOW(), :superuser_id),
('bins', 'Bins view', 2, 4, TRUE, NOW(), :superuser_id);