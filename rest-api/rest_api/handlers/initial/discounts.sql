INSERT INTO discounts (name, code, description, start_date, end_date, percent, min_value, min_quantity, for_categories, for_customers, for_items, currency_id, is_active, created_at, created_by)
VALUES
('Kategoria -10%', 'CAT001', 'Rabat 10% na wybrane kategorie', DATE '2025-01-01', DATE '2026-01-31', 0.10, NULL, NULL, TRUE, FALSE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Kategoria -15% min 200', 'CAT002', 'Rabat 15% dla kategorii przy min 200', DATE '2025-01-01', DATE '2026-01-31', 0.15, 200.00, NULL, TRUE, FALSE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Kategoria -20% min qty 5', 'CAT003', 'Rabat 20% dla kategorii przy min qty 5', DATE '2025-01-01', DATE '2026-01-31', 0.20, NULL, 5, TRUE, FALSE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Kategoria -5% sezon', 'CAT004', 'Sezonowy rabat 5% dla kategorii', DATE '2025-04-01', DATE '2025-09-30', 0.05, NULL, NULL, TRUE, FALSE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Produkt -8%', 'ITM001', 'Rabat 8% na wybrane produkty', DATE '2025-01-01', DATE '2026-01-31', 0.08, NULL, NULL, FALSE, FALSE, TRUE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Produkt -12% min qty 3', 'ITM002', 'Rabat 12% przy min qty 3', DATE '2025-01-01', DATE '2026-01-31', 0.12, NULL, 3, FALSE, FALSE, TRUE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Produkt -20%', 'ITM003', 'Rabat 20% na wybrane produkty', DATE '2025-02-01', DATE '2025-06-30', 0.20, NULL, NULL, FALSE, FALSE, TRUE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Produkt -6% min 100', 'ITM004', 'Rabat 6% przy min wartości 100', DATE '2025-01-01', DATE '2026-01-31', 0.06, 100.00, NULL, FALSE, FALSE, TRUE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Klient -7%', 'CUS001', 'Rabat 7% dla wybranych klientów', DATE '2025-01-01', DATE '2026-01-31', 0.07, NULL, NULL, FALSE, TRUE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Klient -12% VIP', 'CUS002', 'Rabat 12% dla klientów VIP', DATE '2025-01-01', DATE '2026-01-31', 0.12, NULL, NULL, FALSE, TRUE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Klient -5% min 300', 'CUS003', 'Rabat 5% przy min wartości 300', DATE '2025-01-01', DATE '2026-01-31', 0.05, 300.00, NULL, FALSE, TRUE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Klient -18% lojalność', 'CUS004', 'Rabat lojalnościowy 18%', DATE '2025-03-01', DATE '2026-01-31', 0.18, NULL, NULL, FALSE, TRUE, FALSE, 1, TRUE, CURRENT_TIMESTAMP, :superuser_id);
