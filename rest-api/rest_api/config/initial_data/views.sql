INSERT INTO views (key, description, in_menu, "order", controllers, module_id, is_active, created_at, created_by)
VALUES
('groups', 'Groups view', TRUE, 1, ARRAY['GroupController'], 1, TRUE, NOW(), :superuser_id),
('users',  'Users view',  TRUE, 2, ARRAY['UserController'], 1, TRUE, NOW(), :superuser_id);