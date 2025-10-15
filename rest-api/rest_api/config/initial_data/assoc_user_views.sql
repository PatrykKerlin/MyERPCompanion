INSERT INTO user_views (user_id, view_id, can_read, can_modify, is_active, created_at, created_by)
VALUES
(2, 1, TRUE, FALSE, TRUE, NOW(), :superuser_id),
(2, 2, TRUE, FALSE, TRUE, NOW(), :superuser_id),
(2, 3, TRUE, TRUE, TRUE, NOW(), :superuser_id),
(2, 4, TRUE, TRUE, TRUE, NOW(), :superuser_id),
(2, 5, TRUE, TRUE, TRUE, NOW(), :superuser_id);