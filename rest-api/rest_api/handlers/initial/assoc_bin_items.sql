INSERT INTO bin_items (bin_id, item_id, quantity, is_active, created_at, created_by)
VALUES
(3, 1, 40, TRUE, NOW(), :superuser_id),
(3, 2, 800, TRUE, NOW(), :superuser_id),
(3, 3, 600, TRUE, NOW(), :superuser_id);