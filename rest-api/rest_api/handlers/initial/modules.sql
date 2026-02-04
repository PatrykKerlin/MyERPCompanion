INSERT INTO modules (key, description, in_side_menu, "order", is_active, created_at, created_by)
VALUES
('core', 'Core module', FALSE, 0, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('web', 'Web app module', FALSE, 0, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('mobile', 'Mobile app module', FALSE, 0, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('administration', 'Administration module', TRUE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('hr', 'HR module', TRUE, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('logistic', 'Logistic module', TRUE, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('sales', 'Sales module', TRUE, 4, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('purchase', 'Sales module', TRUE, 5, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('accounting', 'Accounting module', TRUE, 6, TRUE, CURRENT_TIMESTAMP, :superuser_id);
