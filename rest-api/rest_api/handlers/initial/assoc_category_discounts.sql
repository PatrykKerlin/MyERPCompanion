INSERT INTO category_discounts (category_id, discount_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(3, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(4, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(5, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(6, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(7, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(8, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(9, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(10, 4, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(11, 4, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(12, 4, TRUE, CURRENT_TIMESTAMP, :superuser_id);
