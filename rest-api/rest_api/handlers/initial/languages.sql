INSERT INTO languages (key, symbol, description, is_active, created_at, created_by)
VALUES
('english', 'en', 'English language', TRUE, NOW(), :superuser_id),
('polish', 'pl', 'Polish language', TRUE, NOW(), :superuser_id);