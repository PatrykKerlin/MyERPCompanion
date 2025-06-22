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
    __toolbar = {
        "hide_menu": "Hide/Show side menu",
        "unlock_form": "Unlock form",
        "delete_record": "Delete record",
    }
    __modules = {
        "administration": "Administration",
    }
    __endpoints = {
        "users": "Users",
        "endpoints": "Endpoints",
        "groups": "Groups",
        "modules": "Modules",
    }
    __views = {
        "marker_tooltip": "Check to search by this field.",
        "id": "Id",
        "key": "Key",
        "description": "Description",
        "save": "Save",
    }
    __errors = {
        "error": "Error",
        "api_not_responding": "API is not responding.",
        "invalid_credentials": "Invalid credentials.",
        "validation_errors": "Validation errors:",
        "record_create_fail": "An error occurred while saving the data.",
        "record_delete_fail": "An error occurred while deleting the data.",
        "record_fetch_fail": "An error occurred while fetching the data.",
    }
    __footer = {
        "connection_status": "Connection status",
        "connected": "Connected",
        "not_connected": "Not connected",
    }
    __messages = {
        "are_you_sure": "Are you sure?",
        "confirm_delete": "This action cannot be undone. Proceed with deletion?",
        "record_deleted_success": "Record deleted successfully.",
        "record_created_success": "Record created successfully.",
        "record_updated_success": "Record updated successfully.",
        "no_records_found": "No matching records found.",
    }

    @property
    def texts(self) -> dict[str, str]:
        dicts = [
            self.__common,
            self.__auth,
            self.__menu_bar,
            self.__toolbar,
            self.__modules,
            self.__endpoints,
            self.__views,
            self.__errors,
            self.__footer,
            self.__messages,
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
