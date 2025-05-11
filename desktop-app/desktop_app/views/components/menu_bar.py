import customtkinter as ctk
import tkinter as tk
from collections.abc import Callable


class MenuBar(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        app_window: ctk.CTk,
        user_label: str,
        user_actions: list[tuple[str, Callable[[], None]]],
    ) -> None:
        super().__init__(master, height=32, fg_color="transparent")
        self._root = app_window
        self.pack(fill="x", side="top")
        self._build_menu_button("Plik", [("Nowy", self._dummy_action), ("Zamknij", master.quit)])
        self._build_menu_button("Edycja", [("Cofnij", self._dummy_action), ("Wklej", self._dummy_action)])
        self._build_menu_button("Pomoc", [("O programie", self._dummy_action)])

        ctk.CTkButton(
            self,
            text=user_label,
            fg_color=None,
            hover_color=("#e0e0e0", "#333333"),
            text_color=None,
            width=120,
            height=28,
            corner_radius=0,
            border_width=0,
            anchor="e",
            command=lambda: self._show_dropdown(self, user_actions, align_right=True),
        ).pack(side="right", padx=10)

    def _build_menu_button(self, label: str, options: list[tuple[str, Callable[[], None]]]) -> None:
        btn = ctk.CTkButton(
            self,
            text=label,
            fg_color="transparent",
            hover_color=("#e0e0e0", "#333333"),
            text_color=None,
            width=80,
            height=28,
            command=lambda: self._show_dropdown(btn, options),
        )
        btn.pack(side="left", padx=2)

    def _show_dropdown(
        self,
        anchor: ctk.CTkBaseClass,
        options: list[tuple[str, Callable[[], None]]],
        align_right: bool = False,
    ) -> None:
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)

        menu_width = 160
        menu_height = len(options) * 32

        x = anchor.winfo_rootx()
        if align_right:
            x = x + anchor.winfo_width() - menu_width
        y = anchor.winfo_rooty() + anchor.winfo_height()
        menu.geometry(f"{menu_width}x{menu_height}+{x}+{y}")

        # zamykanie po kliknięciu poza menu
        def click_outside(event: tk.Event) -> None:
            # jeśli kliknięto poza tym konkretnym menu
            if not str(event.widget).startswith(str(menu)):
                menu.destroy()
                self._root.unbind("<Button-1>", self._menu_binding_id)
                self._root.unbind("<Configure>", self._menu_configure_id)

        # zamykanie przy przesunięciu lub zmianie rozmiaru okna
        def close_menu_on_move(event: tk.Event) -> None:
            menu.destroy()
            self._root.unbind("<Button-1>", self._menu_binding_id)
            self._root.unbind("<Configure>", self._menu_configure_id)

        self._menu_binding_id = self._root.bind("<Button-1>", click_outside)
        self._menu_configure_id = self._root.bind("<Configure>", close_menu_on_move)

        for label, action in options:
            ctk.CTkButton(
                menu,
                text=label,
                width=menu_width,
                height=32,
                fg_color=None,
                corner_radius=0,
                border_width=0,
                hover_color=("#f2f2f2", "#444444"),
                text_color=None,
                anchor="w",
                command=lambda a=action, m=menu: (
                    m.destroy(),
                    self._root.unbind("<Button-1>", self._menu_binding_id),
                    self._root.unbind("<Configure>", self._menu_configure_id),
                    a(),
                ),
            ).pack(fill="x")

    def _dummy_action(self) -> None:
        print("Menu action executed")
