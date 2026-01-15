INSERT INTO discounts (name, code, description, start_date, end_date, percent, amount, min_value, min_quantity, is_active, created_at, created_by)
VALUES
('Category discount 10%', 'CATD001', '10% off for selected categories', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days', 0.10, NULL, NULL, NULL, TRUE, NOW(), :superuser_id),
('Category discount 15% min value', 'CATD002', '15% off for selected categories with min cart value 100', CURRENT_DATE, CURRENT_DATE + INTERVAL '45 days', 0.15, NULL, 100.00, NULL, TRUE, NOW(), :superuser_id),
('Category discount 20% min qty', 'CATD003', '20% off for selected categories with min quantity 3', CURRENT_DATE, CURRENT_DATE + INTERVAL '60 days', 0.20, NULL, NULL, 3, TRUE, NOW(), :superuser_id),
('Item discount 5%', 'ITEMD001', '5% off for selected items', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days', 0.05, NULL, NULL, NULL, TRUE, NOW(), :superuser_id),
('Item discount amount 25', 'ITEMD002', '25 currency units off for selected items', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days', NULL, 25.00, NULL, NULL, TRUE, NOW(), :superuser_id),
('Item discount 12% min qty 2', 'ITEMD003', '12% off for selected items with min quantity 2', CURRENT_DATE, CURRENT_DATE + INTERVAL '45 days', 0.12, NULL, NULL, 2, TRUE, NOW(), :superuser_id),
('Customer discount 7%', 'CUSD001', '7% off for selected customers', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days', 0.07, NULL, NULL, NULL, TRUE, NOW(), :superuser_id),
('Customer discount amount 50 min 300', 'CUSD002', '50 off for selected customers with min cart value 300', CURRENT_DATE, CURRENT_DATE + INTERVAL '60 days', NULL, 50.00, 300.00, NULL, TRUE, NOW(), :superuser_id),
('Customer discount 18% VIP', 'CUSD003', '18% off for VIP customers', CURRENT_DATE, CURRENT_DATE + INTERVAL '90 days', 0.18, NULL, NULL, NULL, TRUE, NOW(), :superuser_id);