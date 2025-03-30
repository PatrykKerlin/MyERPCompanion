INSERT INTO users (username, password, is_superuser, is_active, created_at)
VALUES ('admin', 'admin123', true, true, NOW());

INSERT INTO groups (name, description, is_active, created_at, created_by)
VALUES ('admins', 'Admins', true, NOW(), 1);

INSERT INTO modules (name, label, controller, path, tag, is_active, created_at, created_by)
VALUES ('users', 'Health Check', 'UserController', '', 'Health Check', true, NOW(), 1),
       ('auth', 'Authorization', 'UserController', '/auth', 'Authorization', true, NOW(), 1),
       ('users', 'Users', 'UserController', '/users', 'Users', true, NOW(), 1),
       ('users', 'Groups', 'UserController', '/groups', 'Groups', true, NOW(), 1);

INSERT INTO users_groups (user_id, group_id, is_active, created_at, created_by)
VALUES (1, 1, true, NOW(), 1);

INSERT INTO groups_modules (group_id, module_id, is_active, created_at, created_by)
VALUES (1, 1, true, NOW(), 1);