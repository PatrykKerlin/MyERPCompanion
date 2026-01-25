INSERT INTO user_groups (user_id, group_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 2, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 4, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 5, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 6, TRUE, CURRENT_TIMESTAMP, :superuser_id);