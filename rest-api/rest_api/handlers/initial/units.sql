INSERT INTO units (name, symbol, description, is_active, created_at, created_by)
VALUES
('Gram', 'g', 'Gram unit', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Meter', 'm', 'Meter unit', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Box', 'box', 'Box unit', TRUE, CURRENT_TIMESTAMP, :superuser_id);