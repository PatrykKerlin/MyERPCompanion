INSERT INTO categories (name, description, is_active, created_at, created_by)
VALUES
('Elektronika', 'Urządzenia elektroniczne, akcesoria i komponenty', TRUE, NOW(), :superuser_id),
('Artykuły biurowe', 'Materiały eksploatacyjne i wyposażenie biurowe', TRUE, NOW(), :superuser_id),
('Wyposażenie magazynu', 'Pojemniki, regały i inne akcesoria do magazynów', TRUE, NOW(), :superuser_id);
