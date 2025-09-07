INSERT INTO user_views (user_id, view_id, can_list, can_read, can_create, can_update, can_delete, is_active, created_at, created_by)
VALUES
(2, 1, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, NOW(), :superuser_id),
(2, 2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, NOW(), :superuser_id);