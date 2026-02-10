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
    :superuser_id
FROM parts
WHERE quantity > 0;

UPDATE items i
SET stock_quantity = totals.qty
FROM (
    SELECT item_id, SUM(quantity)::int AS qty
    FROM bin_items
    WHERE is_active IS TRUE
    GROUP BY item_id
) AS totals
WHERE i.id = totals.item_id;
