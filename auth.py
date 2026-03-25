import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class LoginWindow:
    def __init__(self, parent, role, callback):
        self.parent = parent
        self.role = role
        self.callback = callback

        self.window = tk.Toplevel(parent)
        self.window.title(f"Вход - {self.get_role_name()}")
        self.window.geometry("300x250")
        self.window.transient(parent)
        self.window.grab_set()

        self.setup_ui()

    def get_role_name(self):
        roles = {
            'admin': 'Администратор',
            'cashier': 'Кассир',
            'guest': 'Гость'
        }
        return roles.get(self.role, 'Пользователь')

    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.window, text=f"Вход для {self.get_role_name()}",
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=20)

        # Поля ввода
        frame = ttk.Frame(self.window)
        frame.pack(pady=20)

        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=20)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Кнопки
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Войти", command=self.login).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.window.destroy).pack(side="left", padx=5)

        # Для гостя упрощаем вход
        if self.role == 'guest':
            self.username_entry.insert(0, "guest")
            self.password_entry.insert(0, "guest")
            self.username_entry.config(state="disabled")
            self.password_entry.config(state="disabled")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = db.authenticate_user(username, password)

        if user and user['role'] == self.role:
            self.window.destroy()
            self.callback(user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")