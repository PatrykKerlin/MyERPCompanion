INSERT INTO groups (key, description, is_active, created_at, created_by)
VALUES
('admins', 'Admins group', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('hr', 'HR group', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('logistic', 'Logistic group', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('sales', 'Sales group', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('purchase', 'Purchase group', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('accounting', 'Accounting group', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('customers', 'Customers group', TRUE, CURRENT_TIMESTAMP, :superuser_id);