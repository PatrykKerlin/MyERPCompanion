INSERT INTO controllers (name, "table", description, is_active, created_at, created_by)
VALUES
-- business_hr
('DepartmentController', 'departments', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('EmployeeController', 'employees', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('PositionController', 'positions', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),

-- business_logistic
('AssocBinItemController', 'bin_items', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('BinController', 'bins', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('CarrierController', 'carriers', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('CategoryController', 'categories', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('DeliveryMethodController', 'delivery_methods', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ItemController', 'items', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('UnitController', 'units', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('WarehouseController', 'warehouses', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),

-- business_trade
('AssocCategoryDiscountController', 'category_discounts', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AssocCustomerDiscountController', 'customer_discounts', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AssocItemDiscountController', 'item_discounts', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AssocOrderItemController', 'order_items', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AssocOrderStatusController', 'order_statuses', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('CurrencyController', 'currencies', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('CustomerController', 'customers', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('DiscountController', 'discounts', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ExchangeRateController', 'exchange_rates', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('InvoiceController', 'invoices', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OrderController', 'orders', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('OrderViewController', 'orders', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('StatusController', 'statuses', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('SupplierController', 'suppliers', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),

-- core
('AssocModuleGroupController', 'module_groups', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AssocUserGroupController', 'user_groups', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AssocViewControllerController', 'view_controllers', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('AuthController', NULL, NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ControllerController', NULL, NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('CurrentUserController', 'users', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('GroupController', 'groups', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('HealthCheckController', NULL, NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ImageController', 'images', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('LanguageController', 'languages', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ModuleController', 'modules', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ThemeController', 'themes', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('TranslationController', 'translations', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('UserController', 'users', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id),
('ViewController', 'views', NULL, TRUE, CURRENT_TIMESTAMP, :superuser_id);
