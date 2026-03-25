import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from auth import LoginWindow
from admin_window import AdminWindow
from cashier_window import CashierWindow
from guest_window import GuestWindow


class RestaurantApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ресторан - Система управления")
        self.root.geometry("400x300")
        self.current_user = None

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Добро пожаловать в ресторан!",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Кнопки входа
        login_frame = ttk.Frame(self.root)
        login_frame.pack(pady=50)

        ttk.Button(login_frame, text="Вход для администратора",
                   command=lambda: self.login("admin"),
                   width=25).pack(pady=5)

        ttk.Button(login_frame, text="Вход для кассира",
                   command=lambda: self.login("cashier"),
                   width=25).pack(pady=5)

        ttk.Button(login_frame, text="Вход для гостя",
                   command=lambda: self.login("guest"),
                   width=25).pack(pady=5)

        ttk.Button(login_frame, text="Выход",
                   command=self.root.quit,
                   width=25).pack(pady=20)

    def login(self, role):
        login_window = LoginWindow(self.root, role, self.login_callback)

    def login_callback(self, user):
        self.current_user = user
        self.root.withdraw()  # Скрываем главное окно

        if user['role'] == 'admin':
            AdminWindow(self, user)
        elif user['role'] == 'cashier':
            CashierWindow(self, user)
        else:
            GuestWindow(self, user)

    def logout(self):
        self.current_user = None
        self.root.deiconify()  # Показываем главное окно

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = RestaurantApp()
    app.run()