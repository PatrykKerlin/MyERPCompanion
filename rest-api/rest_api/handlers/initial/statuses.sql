INSERT INTO statuses (key, description, "order", is_active, created_at, created_by) VALUES
('new', 'Zamówienie utworzone, oczekuje na dalsze przetwarzanie', 1, TRUE, NOW(), :superuser_id),
('in_progress', 'Zamówienie jest w trakcie przetwarzania', 2, TRUE, NOW(), :superuser_id),
('packed', 'Zamówienie zostało skompletowane i spakowane', 3, TRUE, NOW(), :superuser_id),
('shipped', 'Zamówienie zostało wysłane do klienta', 4, TRUE, NOW(), :superuser_id),
('delivered', 'Zamówienie zostało dostarczone do klienta', 5, TRUE, NOW(), :superuser_id),
('completed', 'Zamówienie zostało zakończone', 6, TRUE, NOW(), :superuser_id),
('on_hold', 'Zamówienie tymczasowo wstrzymane, oczekuje na decyzję', 7, TRUE, NOW(), :superuser_id),
('cancelled', 'Zamówienie zostało anulowane', 8, TRUE, NOW(), :superuser_id);
