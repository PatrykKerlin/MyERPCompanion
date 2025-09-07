INSERT INTO themes (key, is_active, created_at, created_by)
VALUES
('system', TRUE, NOW(), :superuser_id),
('dark',   TRUE, NOW(), :superuser_id),
('light',  TRUE, NOW(), :superuser_id);