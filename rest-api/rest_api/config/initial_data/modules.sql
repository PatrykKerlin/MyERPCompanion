INSERT INTO modules (key, description, in_side_menu, "order", is_active, created_at, created_by)
VALUES
('core', 'Core module', FALSE, 1, TRUE, NOW(), :superuser_id),
('administration', 'Administration module', TRUE, 1, TRUE, NOW(), :superuser_id);