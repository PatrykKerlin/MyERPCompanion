INSERT INTO themes (key, value, is_active, created_at, created_by)
VALUES
('system', 'system', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('dark', 'dark', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('light', 'light', TRUE, CURRENT_TIMESTAMP, :superuser_id);