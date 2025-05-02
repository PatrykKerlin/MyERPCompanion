import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.controller = None

        self.username_entry = ctk.CTkEntry(self, placeholder_text="username")
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.login_button = ctk.CTkButton(self, text="Login", command=self._on_login)
        self.message_label = ctk.CTkLabel(self, text="", wraplength=500)

        self.username_entry.pack(pady=5)
        self.password_entry.pack(pady=5)
        self.login_button.pack(pady=10)
        self.message_label.pack(pady=20)

    def set_controller(self, controller) -> None:
        self.controller = controller

    def _on_login(self) -> None:
        if self.controller:
            username = self.username_entry.get()
            password = self.password_entry.get()
            self.controller.handle_login(username, password)

    def update_message(self, message: str) -> None:
        self.message_label.configure(text=message)
