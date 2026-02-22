INSERT INTO departments (name, description, code, email, phone_number, is_active, created_at, created_by)
VALUES
('IT', 'IT Department', 'IT1', 'it@example.com', '+48987654321', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('HR', 'Human Resources Department', 'HR1', 'hr@example.com', '+48123456780', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Finance', 'Finance and Accounting Department', 'FI1', 'finance@example.com', '+48112233445', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Marketing', 'Marketing and Communications Department', 'MK1', 'marketing@example.com', '+48777777777', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Sales', 'Sales Department', 'SA1', 'sales@example.com', '+48666666666', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Logistics', 'Logistics and Supply Chain Department', 'LO1', 'logistics@example.com', '+48555555555', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('R&D', 'Research and Development Department', 'RD1', 'rnd@example.com', '+48444444444', TRUE, CURRENT_TIMESTAMP, :superuser_id);