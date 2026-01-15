INSERT INTO category_discounts (category_id, discount_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, NOW(), :superuser_id),
(1, 2, TRUE, NOW(), :superuser_id),
(1, 3, TRUE, NOW(), :superuser_id);