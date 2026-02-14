class Translation:
    def __init__(self, items: dict[str, str] | None = None) -> None:
        self.__items = {
            "my_erp_companion": "MyERPCompanion",
            "footer_web_portal": "Web sales portal",
            "all_rights_reserved": "All rights reserved.",
            "api_not_responding": "API is not responding.",
            "loading": "Loading...",
            "data_fetch_fail": "Data fetch failed.",
            "no_permissions": "No permissions.",
            "error": "Error",
            "ok": "OK",
            "username": "User",
            "log_out": "Log out",
            "cart": "Cart",
        }
        if items:
            self.__items.update(items)

    def get(self, key: str) -> str:
        return self.__items.get(key, key)
