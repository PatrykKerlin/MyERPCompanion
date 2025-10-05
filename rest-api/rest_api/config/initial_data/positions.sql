INSERT INTO positions (name, description, level, min_salary, max_salary, currency_id, department_id, is_active, created_at, created_by)
VALUES
('Junior Security Engineer', 'Junior Security Engineer', 1, 8000, 10000, 1, 1, TRUE, NOW(), :superuser_id);