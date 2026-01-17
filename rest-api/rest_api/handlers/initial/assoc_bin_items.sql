INSERT INTO bin_items (bin_id, item_id, quantity, is_active, created_at, created_by)
VALUES
(3, 1, 40, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(3, 2, 800, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(3, 3, 600, TRUE, CURRENT_TIMESTAMP, :superuser_id);