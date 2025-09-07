INSERT INTO modules (key, description, "order", is_active, created_at, created_by)
VALUES
('administration', 'Administration module', 1, TRUE, NOW(), :superuser_id);