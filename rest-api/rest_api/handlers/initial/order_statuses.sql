WITH sales_status_flow AS (
    SELECT id, key, "order"
    FROM statuses
    WHERE key IN ('new', 'approved', 'in_progress', 'packed', 'invoiced')
),
purchase_status_flow AS (
    SELECT id, "order"
    FROM statuses
    WHERE key IN ('new', 'completed')
)
INSERT INTO order_statuses (order_id, status_id, is_active, created_at, created_by)
SELECT
    o.id,
    sf.id AS status_id,
    TRUE,
    o.order_date::timestamp + ((sf."order" - 1) * INTERVAL '2 hours') AS created_at,
    CAST(:superuser_id AS INTEGER)
FROM orders o
JOIN sales_status_flow sf ON o.is_sales IS TRUE
WHERE sf.key <> 'invoiced' OR o.invoice_id IS NOT NULL
UNION ALL
SELECT
    o.id,
    pf.id AS status_id,
    TRUE,
    o.order_date::timestamp + ((pf."order" - 1) * INTERVAL '2 hours') AS created_at,
    CAST(:superuser_id AS INTEGER)
FROM orders o
JOIN purchase_status_flow pf ON o.is_sales IS FALSE
ORDER BY 1, 4;
