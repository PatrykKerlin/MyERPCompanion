INSERT INTO module_groups (group_id, module_id, is_active, created_at, created_by)
VALUES
(1, 1, TRUE, NOW(), :superuser_id);