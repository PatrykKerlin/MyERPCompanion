INSERT INTO bins (location, is_inbound, is_outbound, max_volume, max_weight, warehouse_id, is_active, created_at, created_by)
VALUES
('OUT0101', FALSE, TRUE, 0.5, 500, 1, TRUE, NOW(), :superuser_id),
('OUT0102', FALSE, TRUE, 0.5, 500, 1, TRUE, NOW(), :superuser_id),
('IN0101', TRUE, FALSE, 0.5, 500, 1, TRUE, NOW(), :superuser_id),
('INOUT0101', TRUE, TRUE, 0.5, 500, 1, TRUE, NOW(), :superuser_id);