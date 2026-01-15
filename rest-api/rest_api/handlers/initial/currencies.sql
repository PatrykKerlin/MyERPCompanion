INSERT INTO currencies (code, name, sign, is_active, created_at, created_by)
VALUES
('pln', 'Polski nowy złoty', 'zł', TRUE, NOW(), :superuser_id),
('eur', 'Euro', '€', TRUE, NOW(), :superuser_id),
('usd', 'United States dollar', '$', TRUE, NOW(), :superuser_id);