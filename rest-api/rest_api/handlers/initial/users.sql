INSERT INTO users (username, password, theme, employee_id, customer_id, language_id, is_superuser, is_active, created_at, created_by)
VALUES
('madminowski', :password, 'dark', 1, NULL, 1, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('akadrowa', :password, 'light', 2, NULL, 2, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('phandlowski', :password, 'dark', 3, NULL, 1, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('lzakupski', :password, 'system', 4, NULL, 2, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('plogistyczny', :password, 'system', 5, NULL, 2, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('kksiegowa', :password, 'dark', 6, NULL, 1, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id);

INSERT INTO users (username, password, theme, employee_id, customer_id, language_id, is_superuser, is_active, created_at, created_by)
SELECT
    'customer' || lpad(i::text, 3, '0') AS username,
    :password AS password,
    'dark' AS theme,
    NULL AS employee_id,
    i AS customer_id,
    2 AS language_id,
    FALSE AS is_superuser,
    TRUE AS is_active,
    CURRENT_TIMESTAMP AS created_at,
    :superuser_id AS created_by
FROM generate_series(1, 40) AS s(i);
