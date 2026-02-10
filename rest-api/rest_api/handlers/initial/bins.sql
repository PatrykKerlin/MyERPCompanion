INSERT INTO bins (location, is_inbound, is_outbound, max_volume, max_weight, warehouse_id, is_active, created_at, created_by)
VALUES
('OUT0101', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0102', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0103', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0104', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0105', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0106', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0107', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0108', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0109', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OUT0110', FALSE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('IN0101', TRUE, FALSE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('INOUT0101', TRUE, TRUE, 0.5, 500, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id);
