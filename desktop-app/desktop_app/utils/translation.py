class Translation:
    def __init__(self, items: dict[str, str] | None = None) -> None:
        self.__items = {
            "my_erp_companion": "MyERPCompanion",
            "api_not_responding": "API is not responding.",
            "loading": "Loading...",
        }
        if items:
            self.__items.update(items)

    def get(self, key: str) -> str:
        return self.__items.get(key, key)
