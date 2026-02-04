INSERT INTO user_groups (user_id, group_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 4, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 5, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 6, TRUE, CURRENT_TIMESTAMP, :superuser_id);

INSERT INTO user_groups (user_id, group_id, is_active, created_at, created_by)
SELECT
    u.id,
    7 AS group_id,
    TRUE AS is_active,
    CURRENT_TIMESTAMP AS created_at,
    :superuser_id AS created_by
FROM users u
WHERE u.customer_id IS NOT NULL;
