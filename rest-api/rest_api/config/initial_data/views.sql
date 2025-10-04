INSERT INTO views (key, description, "order", controllers, module_id, is_active, created_at, created_by)
VALUES
('side_menu', 'Side menu view', 1, ARRAY['ModuleController'], 1, TRUE, NOW(), :superuser_id),
('current_user', 'Current user view', 1, ARRAY['CurrentUserController'], 1, TRUE, NOW(), :superuser_id),
('groups', 'Groups view', 1, ARRAY['GroupController'], 2, TRUE, NOW(), :superuser_id),
('users',  'Users view',  2, ARRAY['UserController'], 2, TRUE, NOW(), :superuser_id);