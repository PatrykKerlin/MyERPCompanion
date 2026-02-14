class Translation:
    def __init__(self, items: dict[str, str] | None = None) -> None:
        self.__items = {
            "my_erp_companion": "MyERPCompanion",
            "api_not_responding": "API is not responding.",
            "loading": "Loading...",
            "data_fetch_fail": "Data fetch failed.",
            "no_permissions": "No permissions.",
            "error": "Error",
            "ok": "OK",
            "username": "User",
            "current_user": "Current user",
            "log_out": "Log out",
            "items": "Items",
            "bins": "Bins",
            "bin_transfer": "Bin transfer",
            "order_picking": "Order picking",
            "stock_receiving": "Stock receiving",
        }
        if items:
            self.__items.update(items)

    def get(self, key: str) -> str:
        return self.__items.get(key, key)
