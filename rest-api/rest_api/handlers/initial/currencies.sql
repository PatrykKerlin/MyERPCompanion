INSERT INTO currencies (code, name, sign, is_active, created_at, created_by)
VALUES
('pln', 'Polski nowy złoty', 'zł', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('eur', 'Euro', '€', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('usd', 'United States dollar', '$', TRUE, CURRENT_TIMESTAMP, :superuser_id);