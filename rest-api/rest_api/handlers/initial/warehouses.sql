INSERT INTO warehouses (name, email, phone_number, street, house_number, apartment_number, postal_code, city, country, is_active, created_at, created_by)
VALUES
('Central Warehouse', 'central@company.com', '+48 123 456 789', 'Industrial Street', '12', NULL, '00-123', 'Warsaw', 'Poland', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('North Distribution Center', 'north.dc@company.com', '+48 234 567 890', 'Logistics Avenue', '45', '3A', '80-321', 'Gdańsk', 'Poland', TRUE, CURRENT_TIMESTAMP, :superuser_id),
('South Storage Facility', 'south.storage@company.com', '+48 345 678 901', 'Warehouse Road', '8', NULL, '40-567', 'Katowice', 'Poland', TRUE, CURRENT_TIMESTAMP, :superuser_id);