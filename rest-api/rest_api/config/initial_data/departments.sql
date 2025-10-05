INSERT INTO departments (name, description, code, email, phone_number, is_active, created_at, created_by)
VALUES
('IT', 'IT Department', 'IT1', 'it@example.com', '+48987654321', TRUE, NOW(), :superuser_id);