WITH sales_orders AS (
    SELECT
        o.id,
        o.order_date,
        o.customer_id,
        o.currency_id,
        row_number() OVER (ORDER BY o.order_date, o.id) AS rn,
        random() AS promo_roll,
        CASE
            WHEN o.customer_id <= 8 THEN 1.4
            WHEN o.customer_id <= 20 THEN 1.1
            ELSE 0.9
        END AS customer_weight
    FROM orders o
    WHERE o.is_sales IS TRUE
),
item_counts AS (
    SELECT
        id AS order_id,
        order_date,
        customer_id,
        currency_id,
        customer_weight,
        rn,
        promo_roll,
        GREATEST(
            1,
            LEAST(
                8,
                floor(
                    1
                    + random() * 4
                    + CASE EXTRACT(MONTH FROM order_date)
                        WHEN 11 THEN 1.2
                        WHEN 12 THEN 1.8
                        WHEN 6 THEN 0.8
                        ELSE 0.0
                    END
                    + CASE WHEN customer_id <= 10 THEN 0.9 ELSE 0.0 END
                    + CASE currency_id
                        WHEN 2 THEN 0.3
                        WHEN 3 THEN 0.6
                        ELSE 0.0
                    END
                )::int
            )
        ) AS item_count
    FROM sales_orders
),
item_rows AS (
    SELECT
        ic.order_id,
        ic.order_date,
        ic.customer_id,
        ic.currency_id,
        ic.customer_weight,
        ic.rn,
        ic.promo_roll,
        gs.off
    FROM item_counts ic
    JOIN LATERAL generate_series(0, ic.item_count - 1) AS gs(off) ON TRUE
),
item_data AS (
    SELECT
        ir.order_id,
        ir.order_date,
        ir.customer_id,
        ir.currency_id,
        ir.customer_weight,
        ir.rn,
        ir.off,
        ((ir.rn + ir.off - 1) % 60) + 1 AS item_id,
        random() AS quantity_noise,
        i.purchase_price,
        i.margin,
        i.vat_rate,
        random() AS discount_roll,
        random() AS discount_type_roll,
        CASE
            WHEN ir.promo_roll < 0.35 THEN 0
            WHEN ir.promo_roll < 0.60 THEN 1
            WHEN ir.promo_roll < 0.80 THEN 2
            WHEN ir.promo_roll < 0.95 THEN 3
            ELSE 4
        END AS promo_mode
    FROM item_rows ir
    JOIN items i ON i.id = ((ir.rn + ir.off - 1) % 60) + 1
),
item_pricing AS (
    SELECT
        order_id,
        item_id,
        GREATEST(
            1,
            LEAST(
                24,
                floor(
                    0.5
                    + (1 + (item_id % 6)) * 0.85
                    + CASE EXTRACT(MONTH FROM order_date)
                        WHEN 1 THEN 0.3
                        WHEN 2 THEN 0.2
                        WHEN 5 THEN 0.8
                        WHEN 6 THEN 1.1
                        WHEN 9 THEN 0.7
                        WHEN 10 THEN 0.9
                        WHEN 11 THEN 1.4
                        WHEN 12 THEN 1.8
                        ELSE 0.4
                    END
                    + CASE EXTRACT(DOW FROM order_date)
                        WHEN 0 THEN 0.2
                        WHEN 5 THEN 0.7
                        WHEN 6 THEN 1.0
                        ELSE 0.4
                    END
                    + customer_weight * 1.2
                    + CASE currency_id
                        WHEN 2 THEN 0.6
                        WHEN 3 THEN 1.1
                        ELSE 0.0
                    END
                    + CASE promo_mode
                        WHEN 0 THEN 0.0
                        WHEN 4 THEN 1.8
                        ELSE 0.9
                    END
                    + quantity_noise * 2.4
                )::int
            )
        ) AS quantity,
        purchase_price,
        margin,
        vat_rate,
        CASE
            WHEN promo_mode = 0 THEN 0
            WHEN promo_mode = 4 THEN
                CASE
                    WHEN discount_roll < 0.50 THEN 0.10
                    WHEN discount_roll < 0.82 THEN 0.15
                    WHEN discount_roll < 0.95 THEN 0.20
                    ELSE 0
                END
            WHEN discount_roll < 0.50 THEN 0.05
            WHEN discount_roll < 0.78 THEN 0.10
            WHEN discount_roll < 0.92 THEN 0.15
            ELSE 0
        END AS discount_rate,
        discount_type_roll,
        promo_mode
    FROM item_data
),
insert_sales AS (
    INSERT INTO order_items (
        order_id,
        item_id,
        quantity,
        total_net,
        total_vat,
        total_gross,
        total_discount,
        to_process,
        bin_id,
        category_discount_id,
        customer_discount_id,
        item_discount_id,
        is_active,
        created_at,
        created_by
    )
    SELECT
        order_id,
        item_id,
        quantity,
        ROUND((purchase_price * (1 + margin) * quantity * (1 - discount_rate))::numeric, 2) AS total_net,
        ROUND((purchase_price * (1 + margin) * quantity * (1 - discount_rate) * vat_rate)::numeric, 2) AS total_vat,
        ROUND((purchase_price * (1 + margin) * quantity * (1 - discount_rate) * (1 + vat_rate))::numeric, 2) AS total_gross,
        ROUND((purchase_price * (1 + margin) * quantity * discount_rate)::numeric, 2) AS total_discount,
        1 AS to_process,
        NULL AS bin_id,
        CASE
            WHEN discount_rate > 0
                 AND (
                     promo_mode = 1
                     OR (promo_mode = 4 AND discount_type_roll < 0.33)
                 )
            THEN ((item_id - 1) % 4) + 1
            ELSE NULL
        END AS category_discount_id,
        CASE
            WHEN discount_rate > 0
                 AND (
                     promo_mode = 3
                     OR (promo_mode = 4 AND discount_type_roll >= 0.66)
                 )
            THEN ((item_id - 1) % 4) + 9
            ELSE NULL
        END AS customer_discount_id,
        CASE
            WHEN discount_rate > 0
                 AND (
                     promo_mode = 2
                     OR (promo_mode = 4 AND discount_type_roll >= 0.33 AND discount_type_roll < 0.66)
                 )
            THEN ((item_id - 1) % 4) + 5
            ELSE NULL
        END AS item_discount_id,
        TRUE,
        CURRENT_TIMESTAMP,
        CAST(:superuser_id AS INTEGER)
    FROM item_pricing
    RETURNING order_id
),
purchase_orders AS (
    SELECT id, order_date, row_number() OVER (ORDER BY order_date, id) AS rn
    FROM orders
    WHERE is_sales IS FALSE
),
purchase_counts AS (
    SELECT
        id AS order_id,
        rn,
        (1 + floor(random() * 4))::int AS item_count
    FROM purchase_orders
),
purchase_rows AS (
    SELECT pc.order_id, pc.rn, gs.off
    FROM purchase_counts pc
    JOIN LATERAL generate_series(0, pc.item_count - 1) AS gs(off) ON TRUE
),
purchase_data AS (
    SELECT
        pr.order_id,
        ((pr.rn + pr.off - 1) % 60) + 1 AS item_id,
        (5 + floor(random() * 20))::int AS quantity,
        i.purchase_price,
        i.margin,
        i.vat_rate
    FROM purchase_rows pr
    JOIN items i ON i.id = ((pr.rn + pr.off - 1) % 60) + 1
)
INSERT INTO order_items (
    order_id,
    item_id,
    quantity,
    total_net,
    total_vat,
    total_gross,
    total_discount,
    to_process,
    bin_id,
    category_discount_id,
    customer_discount_id,
    item_discount_id,
    is_active,
    created_at,
    created_by
)
SELECT
    order_id,
    item_id,
    quantity,
    ROUND((purchase_price * (1 + margin) * quantity)::numeric, 2) AS total_net,
    ROUND((purchase_price * (1 + margin) * quantity * vat_rate)::numeric, 2) AS total_vat,
    ROUND((purchase_price * (1 + margin) * quantity * (1 + vat_rate))::numeric, 2) AS total_gross,
    0::numeric AS total_discount,
    quantity AS to_process,
    NULL AS bin_id,
    NULL AS category_discount_id,
    NULL AS customer_discount_id,
    NULL AS item_discount_id,
    TRUE,
    CURRENT_TIMESTAMP,
    CAST(:superuser_id AS INTEGER)
FROM purchase_data;

UPDATE orders o
SET
    total_net = totals.total_net,
    total_vat = totals.total_vat,
    total_gross = totals.total_gross,
    total_discount = totals.total_discount
FROM (
    SELECT
        order_id,
        ROUND(SUM(total_net)::numeric, 2) AS total_net,
        ROUND(SUM(total_vat)::numeric, 2) AS total_vat,
        ROUND(SUM(total_gross)::numeric, 2) AS total_gross,
        ROUND(SUM(total_discount)::numeric, 2) AS total_discount
    FROM order_items
    GROUP BY order_id
) AS totals
WHERE o.id = totals.order_id;

UPDATE order_items
SET to_process = 0;

WITH sold AS (
    SELECT oi.item_id, COALESCE(SUM(oi.quantity), 0)::int AS sold_qty
    FROM order_items oi
    JOIN orders o ON o.id = oi.order_id AND o.is_sales IS TRUE
    GROUP BY oi.item_id
)
UPDATE items i
SET stock_quantity = GREATEST(0, i.stock_quantity - COALESCE(s.sold_qty, 0))
FROM sold s
WHERE i.id = s.item_id;

DELETE FROM bin_items;

WITH outbound_bins AS (
    SELECT id, row_number() OVER (ORDER BY id) AS rn
    FROM bins
    WHERE is_outbound IS TRUE
),
outbound_count AS (
    SELECT COUNT(*)::int AS cnt FROM outbound_bins
),
item_bins AS (
    SELECT
        i.id AS item_id,
        i.stock_quantity,
        ob1.id AS bin_id_1,
        ob2.id AS bin_id_2,
        ob3.id AS bin_id_3
    FROM items i
    CROSS JOIN outbound_count oc
    JOIN outbound_bins ob1 ON ob1.rn = ((i.id - 1) % oc.cnt) + 1
    JOIN outbound_bins ob2 ON ob2.rn = ((i.id + 1) % oc.cnt) + 1
    JOIN outbound_bins ob3 ON ob3.rn = ((i.id + 3) % oc.cnt) + 1
),
parts AS (
    SELECT
        item_id,
        bin_id_1 AS bin_id,
        GREATEST(0, floor(stock_quantity * 0.5))::int AS quantity
    FROM item_bins
    UNION ALL
    SELECT
        item_id,
        bin_id_2 AS bin_id,
        GREATEST(0, floor(stock_quantity * 0.3))::int AS quantity
    FROM item_bins
    UNION ALL
    SELECT
        item_id,
        bin_id_3 AS bin_id,
        (stock_quantity
         - GREATEST(0, floor(stock_quantity * 0.5))
         - GREATEST(0, floor(stock_quantity * 0.3))
        )::int AS quantity
    FROM item_bins
)
INSERT INTO bin_items (bin_id, item_id, quantity, is_active, created_at, created_by)
SELECT
    bin_id,
    item_id,
    quantity,
    TRUE,
    CURRENT_TIMESTAMP,
    CAST(:superuser_id AS INTEGER)
FROM parts
WHERE quantity > 0;
