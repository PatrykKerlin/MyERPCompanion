INSERT INTO languages (key, symbol, description, is_active, created_at, created_by)
VALUES
('english', 'en', 'English language', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('polish', 'pl', 'Polish language', TRUE, CURRENT_TIMESTAMP, :superuser_id);