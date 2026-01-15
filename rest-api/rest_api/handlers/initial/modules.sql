INSERT INTO modules (key, description, in_side_menu, "order", controllers, is_active, created_at, created_by)
VALUES
('core', 'Core module', FALSE, 1, ARRAY['ModuleController', 'CurrentUserController'], TRUE, NOW(), :superuser_id),
('administration', 'Administration module', TRUE, 1, ARRAY['placeholder'], TRUE, NOW(), :superuser_id),
('hr', 'HR module', TRUE, 2, ARRAY['DepartmentController', 'EmployeeController', 'PositionController', 'CurrencyController'], TRUE, NOW(), :superuser_id),
('logistic', 'Logistic module', TRUE, 3, ARRAY['AssocBinItemController', 'BinController', 'CarrierController', 'CategoryController', 'CurrencyController', 'DeliveryMethodController', 'DiscountController', 'ImageController', 'ItemController', 'SupplierController', 'UnitController', 'WarehouseController'], TRUE, NOW(), :superuser_id),
('sales', 'Sales module', TRUE, 4, ARRAY['DiscountController'], TRUE, NOW(), :superuser_id),
('accounting', 'Accounting module', TRUE, 5, ARRAY['CurrencyController'], TRUE, NOW(), :superuser_id);