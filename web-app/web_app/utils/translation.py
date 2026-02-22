class Translation:
    def __init__(self, items: dict[str, str] | None = None) -> None:
        self.__items = {
            "my_erp_companion": "MyERPCompanion",
            "footer_web_portal": "Web sales portal",
            "all_rights_reserved": "All rights reserved.",
            "loading": "Loading...",
            "error": "Error",
            "ok": "OK",
            "api_not_responding": "API is not responding.",
            "no_permissions": "No permissions.",
            "data_fetch_fail": "Data fetch failed.",
        }
        if items:
            self.__items.update(items)

    def get(self, key: str) -> str:
        return self.__items.get(key, key)
