INSERT INTO customer_discounts (customer_id, discount_id, is_active, created_at, created_by)
VALUES
(1, 7, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 8, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 9, TRUE, CURRENT_TIMESTAMP, :superuser_id);