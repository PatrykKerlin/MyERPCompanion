INSERT INTO category_discounts (category_id, discount_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id);