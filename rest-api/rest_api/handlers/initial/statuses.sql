INSERT INTO statuses (name, description, step_number, is_active, created_at, created_by) VALUES
('Nowe', 'Zamówienie utworzone, oczekuje na dalsze przetwarzanie', 1, TRUE, NOW(), :superuser_id),
('W realizacji', 'Zamówienie jest w trakcie przetwarzania', 2, TRUE, NOW(), :superuser_id),
('Wstrzymane', 'Zamówienie tymczasowo wstrzymane, oczekuje na decyzję', 3, TRUE, NOW(), :superuser_id),
('Spakowane', 'Zamówienie zostało skompletowane i spakowane', 4, TRUE, NOW(), :superuser_id),
('Wysłane', 'Zamówienie zostało wysłane do klienta', 5, TRUE, NOW(), :superuser_id),
('Dostarczone', 'Zamówienie zostało dostarczone do klienta', 6, TRUE, NOW(), :superuser_id),
('Anulowane', 'Zamówienie zostało anulowane', 99, TRUE, NOW(), :superuser_id);
