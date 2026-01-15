INSERT INTO categories (name, code, description, is_active, created_at, created_by)
VALUES
('Elektronika', 'EL00001', 'Urządzenia elektroniczne, akcesoria i komponenty', TRUE, NOW(), :superuser_id),
('Artykuły biurowe', 'ARTB001', 'Materiały eksploatacyjne i wyposażenie biurowe', TRUE, NOW(), :superuser_id),
('Wyposażenie magazynu', 'WMAG001', 'Pojemniki, regały i inne akcesoria do magazynów', TRUE, NOW(), :superuser_id);
