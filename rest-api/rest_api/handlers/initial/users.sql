INSERT INTO users (username, password, theme, employee_id, language_id, is_superuser, is_active, created_at, created_by)
VALUES
('user1', :password, 'dark', 1, 2, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id);