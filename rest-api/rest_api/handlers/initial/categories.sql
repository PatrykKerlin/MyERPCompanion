INSERT INTO categories (name, code, description, is_active, created_at, created_by)
VALUES
('Elektronika', 'CAT0001', 'Elektronika użytkowa i komponenty', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Opakowania', 'CAT0002', 'Materiały opakowaniowe i wysyłkowe', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Metalowe', 'CAT0003', 'Elementy metalowe i śruby', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Narzędzia', 'CAT0004', 'Narzędzia ręczne i akcesoria', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Biurowe', 'CAT0005', 'Wyposażenie i materiały biurowe', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Magazyn', 'CAT0006', 'Wyposażenie i akcesoria magazynowe', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('BHP', 'CAT0007', 'Artykuły BHP i bezpieczeństwa', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Automotive', 'CAT0008', 'Części i akcesoria motoryzacyjne', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AGD', 'CAT0009', 'Urządzenia i części AGD', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('IT', 'CAT0010', 'Sprzęt IT i akcesoria', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Chemia', 'CAT0011', 'Chemia techniczna i eksploatacyjna', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Odzież robocza', 'CAT0012', 'Odzież i akcesoria robocze', TRUE, CURRENT_TIMESTAMP, :superuser_id);
