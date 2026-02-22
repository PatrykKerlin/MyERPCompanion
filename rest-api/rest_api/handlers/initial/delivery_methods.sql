INSERT INTO delivery_methods (name, description, price_per_unit, max_width, max_height, max_length, max_weight, carrier_id, unit_id, is_active, created_at, created_by)
VALUES
('Polish Logistics Standard Box', 'Standardowa dostawa w obrębie kraju w ciągu 2 dni roboczych.', 19.90, 0.800, 0.600, 1.200, 30.000, 1, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Polish Logistics Express Box', 'Przyspieszona dostawa krajowa z gwarancją doręczenia następnego dnia.', 34.90, 0.600, 0.500, 1.000, 20.000, 1, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Polish Logistics Same Day', 'Usługa tego samego dnia dla zamówień złożonych do 10:00.', 49.90, 0.500, 0.400, 0.800, 15.000, 1, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Polish Logistics Oversize', 'Transport gabarytów wymagający ręcznej obsługi i dodatkowego zabezpieczenia.', 129.90, 1.500, 1.200, 2.000, 120.000, 1, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('EuroTrans International Air', 'Międzynarodowe przesyłki ekspresowe drogą lotniczą z obsługą celną.', 89.90, 1.200, 1.000, 1.800, 80.000, 2, 3, TRUE, CURRENT_TIMESTAMP, :superuser_id);
