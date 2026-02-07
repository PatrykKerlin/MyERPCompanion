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
            floor(5 + random() * 6)
        )::int AS orders_count
    FROM days
),
series_sales AS (
    SELECT order_date, generate_series(1, orders_count) AS seq
    FROM counts_sales
    WHERE orders_count > 0
),
sales_rolls AS (
    SELECT
        ss.order_date,
        ss.seq,
        random() AS customer_roll,
        random() AS currency_roll,
        random() AS shipping_roll
    FROM series_sales ss
),
sales_profiles AS (
    SELECT
        sr.order_date,
        sr.seq,
        sr.shipping_roll,
        CASE
            WHEN sr.customer_roll < 0.35 THEN (floor(random() * 10) + 1)::int
            WHEN sr.customer_roll < 0.80 THEN (floor(random() * 20) + 11)::int
            ELSE (floor(random() * 10) + 31)::int
        END AS customer_id,
        CASE
            WHEN sr.currency_roll < 0.72 THEN 1
            WHEN sr.currency_roll < 0.90 THEN 2
            ELSE 3
        END AS currency_id
    FROM sales_rolls sr
),
sales_orders AS (
    SELECT
        to_char(sp.order_date, 'YYYY/MM/DD') || '/' ||
        translate(substr(md5(sp.order_date::text || sp.seq::text || 'S'), 1, 3), '0123456789abcdef', 'ABCDEFGHIJKLMNOP') ||
        '/' || lpad(sp.seq::text, 4, '0') AS number,
        TRUE AS is_sales,
        0::numeric(10, 2) AS total_net,
        0::numeric(10, 2) AS total_vat,
        0::numeric(10, 2) AS total_gross,
        0::numeric(10, 2) AS total_discount,
        sp.order_date,
        NULL::text AS tracking_number,
        ROUND(
            (
                8 + sp.shipping_roll * 90
                * CASE sp.currency_id
                    WHEN 1 THEN 1.0
                    WHEN 2 THEN 1.2
                    ELSE 1.35
                END
            )::numeric,
            2
        ) AS shipping_cost,
        NULL::text AS notes,
        NULL::text AS internal_notes,
        sp.customer_id AS customer_id,
        NULL::int AS supplier_id,
        CASE
            WHEN sp.currency_id = 1 THEN (floor(random() * 3) + 1)::int
            ELSE (floor(random() * 2) + 4)::int
        END AS delivery_method_id,
        sp.currency_id AS currency_id,
        NULL::int AS invoice_id,
        TRUE AS is_active,
        CURRENT_TIMESTAMP AS created_at,
        CAST(:superuser_id AS INTEGER) AS created_by
    FROM sales_profiles sp
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
purchase_rolls AS (
    SELECT
        sp.order_date,
        sp.seq,
        random() AS currency_roll,
        random() AS shipping_roll
    FROM series_purchase sp
),
purchase_profiles AS (
    SELECT
        pr.order_date,
        pr.seq,
        pr.shipping_roll,
        CASE
            WHEN pr.currency_roll < 0.55 THEN 1
            WHEN pr.currency_roll < 0.85 THEN 2
            ELSE 3
        END AS currency_id
    FROM purchase_rolls pr
),
purchase_orders AS (
    SELECT
        to_char(pp.order_date, 'YYYYMMDD') ||
        translate(substr(md5(pp.order_date::text || pp.seq::text || 'P'), 1, 7), '0123456789abcdef', 'ABCDEFGHIJKLMNOP') AS number,
        FALSE AS is_sales,
        0::numeric(10, 2) AS total_net,
        0::numeric(10, 2) AS total_vat,
        0::numeric(10, 2) AS total_gross,
        0::numeric(10, 2) AS total_discount,
        pp.order_date,
        translate(substr(md5(pp.order_date::text || pp.seq::text || 'T'), 1, 20), 'abcdef', 'ABCDEF') AS tracking_number,
        ROUND(
            (
                50 + pp.shipping_roll * 450
                * CASE pp.currency_id
                    WHEN 1 THEN 1.0
                    WHEN 2 THEN 1.15
                    ELSE 1.25
                END
            )::numeric,
            2
        ) AS shipping_cost,
        NULL::text AS notes,
        NULL::text AS internal_notes,
        NULL::int AS customer_id,
        (floor(random() * 3) + 1)::int AS supplier_id,
        NULL::int AS delivery_method_id,
        pp.currency_id AS currency_id,
        NULL::int AS invoice_id,
        TRUE AS is_active,
        CURRENT_TIMESTAMP AS created_at,
        CAST(:superuser_id AS INTEGER) AS created_by
    FROM purchase_profiles pp
)
SELECT * FROM sales_orders
UNION ALL
SELECT * FROM purchase_orders;
