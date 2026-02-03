INSERT INTO order_statuses (order_id, status_id, is_active, created_at, created_by)
SELECT
    o.id,
    5 AS status_id,
    TRUE,
    CURRENT_TIMESTAMP,
    :superuser_id
FROM orders o;
