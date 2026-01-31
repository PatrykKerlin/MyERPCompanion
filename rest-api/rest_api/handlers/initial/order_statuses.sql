INSERT INTO order_statuses (order_id, status_id, is_active, created_at, created_by)
SELECT
    o.id,
    CASE
        WHEN o.is_sales IS FALSE THEN 3
        WHEN o.invoice_id IS NOT NULL THEN 5
        WHEN o.order_date >= DATE '2026-01-01' THEN 3
        WHEN o.order_date >= DATE '2025-11-01' THEN 4
        ELSE 4
    END AS status_id,
    TRUE,
    CURRENT_TIMESTAMP,
    :superuser_id
FROM orders o;
