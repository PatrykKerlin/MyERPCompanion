import customtkinter as ctk
from services.core import AuthService
from schemas.core import TokenSchema
from views.core import BaseView
from controllers.core import AppController


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MyERPCompanion")
        self.geometry("1920x1080")

        self.service = AuthService(base_url="http://127.0.0.1:8000/api")
        self.view = BaseView(self)
        self.controller = AppController(service=self.service, view=self.view)

        self.view.set_controller(self.controller)
        self.view.pack(expand=True, fill="both")


class MainApp:
    def __init__(self) -> None:
        self.app = App()

    def run(self) -> None:
        self.app.mainloop()


if __name__ == "__main__":
    MainApp().run()
