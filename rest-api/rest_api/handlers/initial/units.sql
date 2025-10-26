INSERT INTO units (name, symbol, description, is_active, created_at, created_by)
VALUES
('Gram', 'g', 'Gram unit', TRUE, NOW(), :superuser_id),
('Meter', 'm', 'Meter unit', TRUE, NOW(), :superuser_id),
('Box', 'box', 'Box unit', TRUE, NOW(), :superuser_id);