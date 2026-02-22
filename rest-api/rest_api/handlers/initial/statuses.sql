INSERT INTO statuses (key, description, "order", is_active, created_at, created_by)
VALUES
('new', 'Order created, awaiting approval', 1, TRUE, NOW(), :superuser_id),
('approved', 'Order approved and ready for processing', 2, TRUE, NOW(), :superuser_id),
('in_progress', 'Order is being processed', 3, TRUE, NOW(), :superuser_id),
('packed', 'Order has been picked and packed', 4, TRUE, NOW(), :superuser_id),
('invoiced', 'Order has been invoiced', 5, TRUE, NOW(), :superuser_id),
('shipped', 'Order has been shipped to the customer', 6, TRUE, NOW(), :superuser_id),
('delivered', 'Order has been delivered to the customer', 7, TRUE, NOW(), :superuser_id),
('completed', 'Order has been completed', 8, TRUE, NOW(), :superuser_id),
('on_hold', 'Order is temporarily on hold awaiting decision', 9, TRUE, NOW(), :superuser_id),
('cancelled', 'Order has been cancelled', 10, TRUE, NOW(), :superuser_id);
