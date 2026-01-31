INSERT INTO users (username, password, theme, employee_id, language_id, is_superuser, is_active, created_at, created_by)
VALUES
('employee001', :password, 'dark', 1, 2, FALSE, TRUE, CURRENT_TIMESTAMP, :superuser_id);

INSERT INTO users (username, password, theme, employee_id, language_id, is_superuser, is_active, created_at, created_by)
SELECT
    'customer' || lpad(i::text, 3, '0') AS username,
    :password AS password,
    'dark' AS theme,
    NULL AS employee_id,
    2 AS language_id,
    FALSE AS is_superuser,
    TRUE AS is_active,
    CURRENT_TIMESTAMP AS created_at,
    :superuser_id AS created_by
FROM generate_series(1, 40) AS s(i);
