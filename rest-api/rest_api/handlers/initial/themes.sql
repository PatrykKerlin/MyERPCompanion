INSERT INTO themes (key, value, is_active, created_at, created_by)
VALUES
('system', 'system', TRUE, NOW(), :superuser_id),
('dark', 'dark', TRUE, NOW(), :superuser_id),
('light', 'light', TRUE, NOW(), :superuser_id);