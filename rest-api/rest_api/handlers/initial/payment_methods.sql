INSERT INTO payment_methods (name, description, provider, api_url, surcharge_percent, is_active, created_at, created_by)
VALUES
('Przelew bankowy', 'Standardowy przelew bankowy na rachunek sprzedawcy', 'bank_transfer', 'https://bank.example.com/api/payments', 0, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Karta płatnicza', 'Płatność kartą debetową lub kredytową', 'stripe', 'https://api.stripe.com/v1/charges', 0.02, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('PayPal', 'Płatność online przez PayPal', 'paypal', 'https://api.paypal.com/v2/checkout/orders', 0.05, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('Płatność przy odbiorze', 'Gotówka lub karta przy odbiorze przesyłki', 'cash_on_delivery', 'https://logistics.example.com/api/cod', 0, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('BLIK', 'Płatność mobilna BLIK', 'blik', 'https://api.blik.com/payments', 0.035, TRUE, CURRENT_TIMESTAMP, :superuser_id);
