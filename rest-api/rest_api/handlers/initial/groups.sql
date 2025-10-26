INSERT INTO groups (key, description, is_active, created_at, created_by)
VALUES
('admins', 'Admins group', TRUE, NOW(), :superuser_id),
('hr', 'HR group', TRUE, NOW(), :superuser_id),
('logistic', 'Logistic group', TRUE, NOW(), :superuser_id);