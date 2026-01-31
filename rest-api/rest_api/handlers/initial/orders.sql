INSERT INTO orders (
    number,
    is_sales,
    total_net,
    total_vat,
    total_gross,
    total_discount,
    order_date,
    tracking_number,
    shipping_cost,
    notes,
    internal_notes,
    customer_id,
    supplier_id,
    delivery_method_id,
    currency_id,
    invoice_id,
    is_active,
    created_at,
    created_by
)
WITH days AS (
    SELECT generate_series(DATE '2025-01-01', DATE '2026-01-31', INTERVAL '1 day')::date AS order_date
),
counts_sales AS (
    SELECT
        order_date,
        GREATEST(
            0,
            floor(
                random() * 12
                * CASE EXTRACT(MONTH FROM order_date)
                    WHEN 1 THEN 0.9
                    WHEN 2 THEN 0.85
                    WHEN 3 THEN 0.95
                    WHEN 4 THEN 1.05
                    WHEN 5 THEN 1.15
                    WHEN 6 THEN 1.25
                    WHEN 7 THEN 0.9
                    WHEN 8 THEN 0.85
                    WHEN 9 THEN 1.05
                    WHEN 10 THEN 1.25
                    WHEN 11 THEN 1.6
                    WHEN 12 THEN 1.9
                    ELSE 1.0
                END
                * CASE EXTRACT(DOW FROM order_date)
                    WHEN 0 THEN 0.6
                    WHEN 6 THEN 0.7
                    ELSE 1.0
                END
            )
        )::int AS orders_count
    FROM days
),
series_sales AS (
    SELECT order_date, generate_series(1, orders_count) AS seq
    FROM counts_sales
    WHERE orders_count > 0
),
sales_orders AS (
    SELECT
        to_char(order_date, 'YYYY/MM/DD') || '/' ||
        translate(substr(md5(order_date::text || seq::text || 'S'), 1, 3), '0123456789abcdef', 'ABCDEFGHIJKLMNOP') ||
        '/' || lpad(seq::text, 4, '0') AS number,
        TRUE AS is_sales,
        0::numeric(10, 2) AS total_net,
        0::numeric(10, 2) AS total_vat,
        0::numeric(10, 2) AS total_gross,
        0::numeric(10, 2) AS total_discount,
        order_date,
        NULL::text AS tracking_number,
        ROUND((10 + random() * 70)::numeric, 2) AS shipping_cost,
        NULL::text AS notes,
        NULL::text AS internal_notes,
        (floor(random() * 40) + 1)::int AS customer_id,
        NULL::int AS supplier_id,
        (floor(random() * 5) + 1)::int AS delivery_method_id,
        1 AS currency_id,
        NULL::int AS invoice_id,
        TRUE AS is_active,
        CURRENT_TIMESTAMP AS created_at,
        CAST(:superuser_id AS INTEGER) AS created_by
    FROM series_sales
),
counts_purchase AS (
    SELECT
        order_date,
        (floor(random() * 3))::int AS orders_count
    FROM days
),
series_purchase AS (
    SELECT order_date, generate_series(1, orders_count) AS seq
    FROM counts_purchase
    WHERE orders_count > 0
),
purchase_orders AS (
    SELECT
        to_char(order_date, 'YYYYMMDD') ||
        translate(substr(md5(order_date::text || seq::text || 'P'), 1, 7), '0123456789abcdef', 'ABCDEFGHIJKLMNOP') AS number,
        FALSE AS is_sales,
        0::numeric(10, 2) AS total_net,
        0::numeric(10, 2) AS total_vat,
        0::numeric(10, 2) AS total_gross,
        0::numeric(10, 2) AS total_discount,
        order_date,
        translate(substr(md5(order_date::text || seq::text || 'T'), 1, 20), 'abcdef', 'ABCDEF') AS tracking_number,
        ROUND((50 + random() * 450)::numeric, 2) AS shipping_cost,
        NULL::text AS notes,
        NULL::text AS internal_notes,
        NULL::int AS customer_id,
        (floor(random() * 3) + 1)::int AS supplier_id,
        NULL::int AS delivery_method_id,
        1 AS currency_id,
        NULL::int AS invoice_id,
        TRUE AS is_active,
        CURRENT_TIMESTAMP AS created_at,
        CAST(:superuser_id AS INTEGER) AS created_by
    FROM series_purchase
)
SELECT * FROM sales_orders
UNION ALL
SELECT * FROM purchase_orders;
