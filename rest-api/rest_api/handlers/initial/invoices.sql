WITH max_sales AS (
    SELECT max(order_date) AS max_date
    FROM orders
    WHERE is_sales IS TRUE
),
invoiced_orders AS (
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
    CROSS JOIN max_sales ms
    WHERE
        o.is_sales IS TRUE
        AND o.order_date <= (ms.max_date - INTERVAL '5 days')
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
