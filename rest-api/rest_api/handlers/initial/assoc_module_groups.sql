INSERT INTO module_groups (group_id, module_id, can_read, can_modify, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 2, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 3, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 4, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 5, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 6, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(1, 7, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 1, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(2, 3, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(3, 1, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(3, 4, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(4, 1, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(4, 5, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(5, 1, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(5, 6, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(6, 1, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id),
(6, 7, TRUE, TRUE, TRUE, CURRENT_TIMESTAMP, :superuser_id);
