INSERT INTO user_groups (user_id, group_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, NOW(), :superuser_id),
(2, 2, TRUE, NOW(), :superuser_id);