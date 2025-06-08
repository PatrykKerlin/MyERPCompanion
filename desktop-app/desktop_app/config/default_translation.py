class DefaultTranslation:
    __common = {
        "myerpcompanion": "MyERPCompanion",
        "loading": "Loading",
        "cancel": "Cancel",
        "ok": "OK",
        "search": "Search",
        "back": "Back",
    }
    __auth = {
        "login": "Login",
        "log_in": "Log in",
        "username": "Username",
        "password": "Password",
    }
    __menu_bar = {
        "file": "File",
        "new": "New",
        "open": "Open",
        "exit": "Exit",
        "edit": "Edit",
        "help": "Help",
        "undo": "Undo",
        "redo": "Redo",
        "about": "About",
    }
    __buttons_bar = {
        "hide_menu": "Hide/Show side menu",
    }
    __modules = {
        "administration": "Administration",
    }
    __endpoints = {
        "users": "Users",
        "endpoints": "Endpoints",
        "groups": "Groups",
        "groups_{id}": "Group: {key}",
        "groups_1": "<TEST>",
        "modules": "Modules",
    }
    __views = {
        "marker_tooltip": "Check to search by this field.",
        "id": "Id",
        "key": "Key",
        "description": "Description",
    }
    __errors = {
        "api_not_responding": "API is not responding.",
        "invalid_credentials": "Invalid credentials.",
    }
    __footer = {
        "connection_status": "Connection status",
        "connected": "Connected",
        "not_connected": "Not connected",
    }

    @property
    def texts(self) -> dict[str, str]:
        dicts = [
            self.__common,
            self.__auth,
            self.__menu_bar,
            self.__buttons_bar,
            self.__modules,
            self.__endpoints,
            self.__views,
            self.__errors,
            self.__footer,
        ]
        result: dict[str, str] = {}
        duplicates: set[str] = set()
        for item in dicts:
            for key, value in item.items():
                if key in result.keys():
                    duplicates.add(key)
                result[key] = value
        if duplicates:
            raise ValueError(f"Duplicate translation keys found: {duplicates}")
        return result
