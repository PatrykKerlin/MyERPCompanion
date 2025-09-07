INSERT INTO users (username, password, employee_id, language_id, theme_id, is_superuser, is_active, created_at, created_by)
VALUES
('user1', :password, NULL, 2, 2, FALSE, TRUE, NOW(), :superuser_id);