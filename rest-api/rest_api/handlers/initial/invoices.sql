WITH invoiced_orders AS (
    SELECT
        o.id AS order_id,
        o.order_date,
        o.customer_id,
        o.currency_id,
        o.total_net,
        o.total_vat,
        o.total_gross,
        o.total_discount,
        (o.order_date + INTERVAL '1 day')::date AS issue_date,
        c.payment_term,
        row_number() OVER (
            PARTITION BY (o.order_date + INTERVAL '1 day')::date
            ORDER BY o.order_date, o.id
        ) AS seq
    FROM orders o
    JOIN customers c ON c.id = o.customer_id
    WHERE
        o.is_sales IS TRUE
),
inserted AS (
    INSERT INTO invoices (
        number,
        issue_date,
        due_date,
        is_paid,
        total_net,
        total_vat,
        total_gross,
        total_discount,
        notes,
        customer_id,
        currency_id,
        is_active,
        created_at,
        created_by
    )
    SELECT
        to_char(issue_date, 'YYYY/MM/DD') || '/' || lpad(seq::text, 4, '0') AS number,
        issue_date,
        (issue_date + (payment_term || ' days')::interval)::date AS due_date,
        (issue_date <= (CURRENT_DATE - INTERVAL '45 days')) AS is_paid,
        total_net,
        total_vat,
        total_gross,
        total_discount,
        NULL AS notes,
        customer_id,
        currency_id,
        TRUE,
        CURRENT_TIMESTAMP,
        :superuser_id
    FROM invoiced_orders
    RETURNING id, number
)
UPDATE orders o
SET invoice_id = i.id
FROM invoiced_orders io
JOIN inserted i
    ON i.number = to_char(io.issue_date, 'YYYY/MM/DD') || '/' || lpad(io.seq::text, 4, '0')
WHERE o.id = io.order_id;

WITH ranked_sales_orders AS (
    SELECT
        o.id,
        o.customer_id,
        row_number() OVER (PARTITION BY o.customer_id ORDER BY o.id DESC) AS rn
    FROM orders o
    WHERE
        o.is_sales IS TRUE
        AND o.customer_id IS NOT NULL
)
UPDATE orders o
SET invoice_id = NULL
FROM ranked_sales_orders rso
WHERE
    o.id = rso.id
    AND rso.rn = 1;

WITH ranked_sales_orders AS (
    SELECT
        o.id,
        o.customer_id,
        row_number() OVER (PARTITION BY o.customer_id ORDER BY o.id DESC) AS rn
    FROM orders o
    WHERE
        o.is_sales IS TRUE
        AND o.customer_id IS NOT NULL
)
UPDATE invoices i
SET
    is_paid = TRUE,
    due_date = (CURRENT_DATE - INTERVAL '10 days')::date
FROM ranked_sales_orders rso
JOIN orders o ON o.id = rso.id
WHERE
    rso.rn = 2
    AND o.invoice_id = i.id;

WITH ranked_sales_orders AS (
    SELECT
        o.id,
        o.customer_id,
        row_number() OVER (PARTITION BY o.customer_id ORDER BY o.id DESC) AS rn
    FROM orders o
    WHERE
        o.is_sales IS TRUE
        AND o.customer_id IS NOT NULL
)
UPDATE invoices i
SET
    is_paid = FALSE,
    due_date = (CURRENT_DATE + INTERVAL '14 days')::date
FROM ranked_sales_orders rso
JOIN orders o ON o.id = rso.id
WHERE
    rso.rn = 3
    AND o.invoice_id = i.id;

WITH ranked_sales_orders AS (
    SELECT
        o.id,
        o.customer_id,
        row_number() OVER (PARTITION BY o.customer_id ORDER BY o.id DESC) AS rn
    FROM orders o
    WHERE
        o.is_sales IS TRUE
        AND o.customer_id IS NOT NULL
)
UPDATE invoices i
SET
    is_paid = FALSE,
    due_date = (CURRENT_DATE - INTERVAL '14 days')::date
FROM ranked_sales_orders rso
JOIN orders o ON o.id = rso.id
WHERE
    rso.rn = 4
    AND o.invoice_id = i.id;
