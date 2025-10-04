INSERT INTO groups (key, description, is_active, created_at, created_by)
VALUES
('admins', 'Administration', TRUE, NOW(), :superuser_id),
('hr', 'Human Resources', TRUE, NOW(), :superuser_id),
('logistic', 'Logistic', TRUE, NOW(), :superuser_id),
('sales', 'Sales', TRUE, NOW(), :superuser_id);