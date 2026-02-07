WITH status_flow AS (
    SELECT id, "order"
    FROM statuses
    WHERE key IN ('new', 'approved', 'in_progress', 'packed', 'invoiced')
)
INSERT INTO order_statuses (order_id, status_id, is_active, created_at, created_by)
SELECT
    o.id,
    sf.id AS status_id,
    TRUE,
    o.order_date::timestamp + ((sf."order" - 1) * INTERVAL '2 hours') AS created_at,
    CAST(:superuser_id AS INTEGER)
FROM orders o
JOIN status_flow sf ON TRUE
ORDER BY o.id, sf."order";
