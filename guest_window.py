import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import db


class GuestWindow:
    def __init__(self, app, user):
        self.app = app
        self.user = user
        self.current_order_id = None

        self.window = tk.Toplevel(app.root)
        self.window.title(f"Меню гостя - {user['username']}")
        self.window.geometry("900x600")

        self.setup_menu()
        self.setup_ui()

    def setup_menu(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выйти", command=self.logout)

    def setup_ui(self):
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка меню
        self.menu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.menu_frame, text="Меню")
        self.setup_menu_view()

        # Вкладка создания заказа
        self.create_order_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.create_order_frame, text="Создать заказ")
        self.setup_create_order()

        # Вкладка статуса заказа
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="Статус заказа")
        self.setup_status_view()

    def setup_menu_view(self):
        # Категории
        category_frame = ttk.Frame(self.menu_frame)
        category_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(category_frame, text="Категория:").pack(side="left", padx=5)
        self.view_category_combo = ttk.Combobox(category_frame, width=20)
        self.view_category_combo.pack(side="left", padx=5)
        self.view_category_combo.bind('<<ComboboxSelected>>', self.filter_view_menu)

        # Таблица меню
        columns = ("id", "name", "description", "price", "category")
        self.view_menu_tree = ttk.Treeview(self.menu_frame, columns=columns, show="headings", height=20)

        self.view_menu_tree.heading("id", text="ID")
        self.view_menu_tree.heading("name", text="Название")
        self.view_menu_tree.heading("description", text="Описание")
        self.view_menu_tree.heading("price", text="Цена")
        self.view_menu_tree.heading("category", text="Категория")

        self.view_menu_tree.column("id", width=50)
        self.view_menu_tree.column("name", width=150)
        self.view_menu_tree.column("description", width=300)
        self.view_menu_tree.column("price", width=80)
        self.view_menu_tree.column("category", width=100)

        scrollbar = ttk.Scrollbar(self.menu_frame, orient="vertical", command=self.view_menu_tree.yview)
        self.view_menu_tree.configure(yscrollcommand=scrollbar.set)

        self.view_menu_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Загрузка категорий и меню
        self.load_categories_for_view()
        self.refresh_view_menu()

    def load_categories_for_view(self):
        categories = db.get_menu_categories()
        category_list = [cat['category'] for cat in categories]
        self.view_category_combo['values'] = ['Все'] + category_list
        self.view_category_combo.set('Все')

    def filter_view_menu(self, event=None):
        self.refresh_view_menu()

    def refresh_view_menu(self):
        for item in self.view_menu_tree.get_children():
            self.view_menu_tree.delete(item)

        category = self.view_category_combo.get()
        if category == 'Все':
            menu_items = db.get_menu()
        else:
            menu_items = db.get_menu(category)

        for item in menu_items:
            self.view_menu_tree.insert("", "end", values=(
                item['id'], item['name'], item['description'],
                f"{item['price']:.2f}", item['category']
            ))

    def setup_create_order(self):
        # Фрейм для информации о заказе
        info_frame = ttk.LabelFrame(self.create_order_frame, text="Ваши данные")
        info_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(info_frame, text="Ваше имя:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.guest_name_entry = ttk.Entry(info_frame, width=30)
        self.guest_name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(info_frame, text="Номер стола:").grid(row=0, column=2, sticky="w", pady=5, padx=5)
        self.table_number_entry = ttk.Entry(info_frame, width=10)
        self.table_number_entry.grid(row=0, column=3, pady=5, padx=5)

        # Фрейм для выбора блюд
        menu_frame = ttk.LabelFrame(self.create_order_frame, text="Меню")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Левая часть - список блюд
        left_frame = ttk.Frame(menu_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Категории
        category_frame = ttk.Frame(left_frame)
        category_frame.pack(fill="x", pady=5)

        ttk.Label(category_frame, text="Категория:").pack(side="left", padx=5)
        self.create_category_combo = ttk.Combobox(category_frame, width=20)
        self.create_category_combo.pack(side="left", padx=5)
        self.create_category_combo.bind('<<ComboboxSelected>>', self.filter_create_menu)

        # Таблица меню
        columns = ("id", "name", "price", "category")
        self.create_menu_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)

        self.create_menu_tree.heading("id", text="ID")
        self.create_menu_tree.heading("name", text="Название")
        self.create_menu_tree.heading("price", text="Цена")
        self.create_menu_tree.heading("category", text="Категория")

        self.create_menu_tree.column("id", width=50)
        self.create_menu_tree.column("name", width=200)
        self.create_menu_tree.column("price", width=80)
        self.create_menu_tree.column("category", width=100)

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.create_menu_tree.yview)
        self.create_menu_tree.configure(yscrollcommand=scrollbar.set)

        self.create_menu_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Правая часть - корзина
        right_frame = ttk.LabelFrame(menu_frame, text="Корзина")
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Таблица корзины
        cart_columns = ("menu_id", "name", "quantity", "price", "subtotal")
        self.cart_tree = ttk.Treeview(right_frame, columns=cart_columns, show="headings", height=15)

        self.cart_tree.heading("menu_id", text="ID")
        self.cart_tree.heading("name", text="Название")
        self.cart_tree.heading("quantity", text="Кол-во")
        self.cart_tree.heading("price", text="Цена")
        self.cart_tree.heading("subtotal", text="Сумма")

        self.cart_tree.column("menu_id", width=50)
        self.cart_tree.column("name", width=150)
        self.cart_tree.column("quantity", width=70)
        self.cart_tree.column("price", width=80)
        self.cart_tree.column("subtotal", width=100)

        cart_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)

        self.cart_tree.pack(side="left", fill="both", expand=True)
        cart_scrollbar.pack(side="right", fill="y")

        # Кнопки управления корзиной
        cart_buttons = ttk.Frame(right_frame)
        cart_buttons.pack(pady=5)

        ttk.Button(cart_buttons, text="Добавить", command=self.add_to_cart).pack(side="left", padx=5)
        ttk.Button(cart_buttons, text="Удалить", command=self.remove_from_cart).pack(side="left", padx=5)
        ttk.Button(cart_buttons, text="Очистить", command=self.clear_cart).pack(side="left", padx=5)

        # Кнопки управления заказом
        order_buttons = ttk.Frame(self.create_order_frame)
        order_buttons.pack(pady=10)

        ttk.Button(order_buttons, text="Создать заказ", command=self.create_order, width=20).pack(side="left", padx=5)
        ttk.Button(order_buttons, text="Очистить форму", command=self.clear_create_order_form, width=20).pack(
            side="left", padx=5)

        # Загрузка данных
        self.load_categories_for_create()
        self.refresh_create_menu()
        self.cart_items = []

    def load_categories_for_create(self):
        categories = db.get_menu_categories()
        category_list = [cat['category'] for cat in categories]
        self.create_category_combo['values'] = ['Все'] + category_list
        self.create_category_combo.set('Все')

    def filter_create_menu(self, event=None):
        self.refresh_create_menu()

    def refresh_create_menu(self):
        for item in self.create_menu_tree.get_children():
            self.create_menu_tree.delete(item)

        category = self.create_category_combo.get()
        if category == 'Все':
            menu_items = db.get_menu()
        else:
            menu_items = db.get_menu(category)

        for item in menu_items:
            self.create_menu_tree.insert("", "end", values=(
                item['id'], item['name'], f"{item['price']:.2f}", item['category']
            ))

    def add_to_cart(self):
        selected = self.create_menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо")
            return

        item = self.create_menu_tree.item(selected[0])['values']

        for cart_item in self.cart_items:
            if cart_item['menu_id'] == item[0]:
                cart_item['quantity'] += 1
                self.update_cart_display()
                return

        self.cart_items.append({
            'menu_id': item[0],
            'name': item[1],
            'quantity': 1,
            'price': float(item[2])
        })
        self.update_cart_display()

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            return

        item = self.cart_tree.item(selected[0])['values']
        menu_id = item[0]

        self.cart_items = [i for i in self.cart_items if i['menu_id'] != menu_id]
        self.update_cart_display()

    def clear_cart(self):
        self.cart_items = []
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0
        for item in self.cart_items:
            subtotal = item['quantity'] * item['price']
            total += subtotal
            self.cart_tree.insert("", "end", values=(
                item['menu_id'], item['name'], item['quantity'],
                f"{item['price']:.2f}", f"{subtotal:.2f}"
            ))

        if hasattr(self, 'total_label'):
            self.total_label.config(text=f"Итого: {total:.2f} руб.")
        else:
            self.total_label = ttk.Label(self.create_order_frame, text=f"Итого: {total:.2f} руб.",
                                         font=("Arial", 12, "bold"))
            self.total_label.pack(pady=5)
        self.total_label.config(text=f"Итого: {total:.2f} руб.")

    def create_order(self):
        guest_name = self.guest_name_entry.get()
        table_number = self.table_number_entry.get()

        if not guest_name:
            messagebox.showwarning("Предупреждение", "Введите ваше имя")
            return

        if not self.cart_items:
            messagebox.showwarning("Предупреждение", "Добавьте блюда в заказ")
            return

        try:
            table_number = int(table_number) if table_number else None
        except ValueError:
            messagebox.showerror("Ошибка", "Номер стола должен быть числом")
            return

        order_items = []
        for item in self.cart_items:
            order_items.append({
                'menu_id': item['menu_id'],
                'quantity': item['quantity'],
                'price': item['price']
            })

        order_id = db.create_order(guest_name, table_number, order_items)

        if order_id:
            self.current_order_id = order_id
            messagebox.showinfo("Успех", f"Ваш заказ №{order_id} принят!")
            self.clear_create_order_form()
            self.notebook.select(self.status_frame)
            self.check_order_status()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать заказ")

    def clear_create_order_form(self):
        self.guest_name_entry.delete(0, tk.END)
        self.table_number_entry.delete(0, tk.END)
        self.cart_items = []
        self.update_cart_display()

    def setup_status_view(self):
        # Фрейм для ввода номера заказа
        search_frame = ttk.LabelFrame(self.status_frame, text="Поиск заказа")
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Номер заказа:").pack(side="left", padx=5)
        self.order_id_entry = ttk.Entry(search_frame, width=10)
        self.order_id_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Проверить", command=self.check_order_status).pack(side="left", padx=5)

        # Фрейм для отображения статуса
        status_frame = ttk.LabelFrame(self.status_frame, text="Статус заказа")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.status_label = ttk.Label(status_frame, text="", font=("Arial", 14))
        self.status_label.pack(pady=20)

        # Детали заказа
        self.details_text = scrolledtext.ScrolledText(status_frame, height=15, width=60)
        self.details_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Кнопка обновления
        ttk.Button(status_frame, text="Обновить", command=self.check_order_status).pack(pady=10)

    def check_order_status(self):
        order_id = self.order_id_entry.get() or self.current_order_id

        if not order_id:
            messagebox.showwarning("Предупреждение", "Введите номер заказа")
            return

        try:
            order_id = int(order_id)
        except ValueError:
            messagebox.showerror("Ошибка", "Номер заказа должен быть числом")
            return

        order_details = db.get_order_details(order_id)

        if not order_details:
            self.status_label.config(text="Заказ не найден")
            self.details_text.delete(1.0, tk.END)
            return

        order = order_details[0]
        status_text = self.get_status_text(order['status'])

        status_colors = {
            'pending': 'orange',
            'preparing': 'blue',
            'ready': 'green',
            'delivered': 'gray'
        }

        self.status_label.config(text=f"Статус: {status_text}", foreground=status_colors.get(order['status'], 'black'))

        # Формируем детали заказа
        details = f"""
        ╔════════════════════════════════════════════════════════════╗
        ║                    ДЕТАЛИ ЗАКАЗА №{order_id}                ║
        ╠════════════════════════════════════════════════════════════╣
        ║ Гость: {order['guest_name']}
        ║ Стол: {order['table_number'] or 'Не указан'}
        ║ Время создания: {order['created_at']}
        ╠════════════════════════════════════════════════════════════╣
        ║                       Состав заказа:                       ║
        """

        total = 0
        for item in order_details:
            if item['item_id']:
                subtotal = item['quantity'] * item['price']
                total += subtotal
                details += f"""
        ║ {item['item_name']:<30}
        ║   {item['quantity']} x {item['price']:.2f} = {subtotal:.2f} руб.
        """

        details += f"""
        ╠════════════════════════════════════════════════════════════╣
        ║ ИТОГО: {total:.2f} руб.
        ╚════════════════════════════════════════════════════════════╝
        """

        if order['status'] == 'ready':
            details += "\n\nВаш заказ готов! Подойдите к кассе для получения."
        elif order['status'] == 'delivered':
            details += "\n\nЗаказ выдан. Спасибо за посещение!"

        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.config(state="disabled")

    def get_status_text(self, status):
        statuses = {
            'pending': 'В обработке',
            'preparing': 'Готовится',
            'ready': 'Готов к выдаче',
            'delivered': 'Выдан',
            'cancelled': 'Отменен'
        }
        return statuses.get(status, status)

    def logout(self):
        self.window.destroy()
        self.app.logout()