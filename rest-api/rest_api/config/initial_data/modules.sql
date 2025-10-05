INSERT INTO modules (key, description, in_side_menu, "order", is_active, created_at, created_by)
VALUES
('core', 'Core module', FALSE, 1, TRUE, NOW(), :superuser_id),
('administration', 'Administration module', TRUE, 1, TRUE, NOW(), :superuser_id),
('hr', 'HR module', TRUE, 2, TRUE, NOW(), :superuser_id),
('warehouse', 'Warehouse module', TRUE, 3, TRUE, NOW(), :superuser_id),
('logistic', 'Logistic module', TRUE, 3, TRUE, NOW(), :superuser_id),
('procurement', 'Procurement module', TRUE, 4, TRUE, NOW(), :superuser_id),
('sales', 'Sales module', TRUE, 5, TRUE, NOW(), :superuser_id),
('finance', 'Finance module', TRUE, 6, TRUE, NOW(), :superuser_id);