INSERT INTO item_discounts (item_id, discount_id, is_active, created_at, created_by)
VALUES
(1, 4, TRUE, NOW(), :superuser_id),
(1, 5, TRUE, NOW(), :superuser_id),
(1, 6, TRUE, NOW(), :superuser_id);