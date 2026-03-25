import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import db


class CashierWindow:
    def __init__(self, app, user):
        self.app = app
        self.user = user

        self.window = tk.Toplevel(app.root)
        self.window.title(f"Панель кассира - {user['username']}")
        self.window.geometry("1000x700")

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

        # Вкладка заказов
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self.setup_orders_view()

        # Вкладка создания заказа
        self.create_order_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.create_order_frame, text="Создать заказ")
        self.setup_create_order()

    def setup_orders_view(self):
        # Таблица заказов
        columns = ("id", "guest_name", "table_number", "total_amount", "status", "created_at")
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=columns, show="headings", height=15)

        self.orders_tree.heading("id", text="№ заказа")
        self.orders_tree.heading("guest_name", text="Имя гостя")
        self.orders_tree.heading("table_number", text="Стол")
        self.orders_tree.heading("total_amount", text="Сумма")
        self.orders_tree.heading("status", text="Статус")
        self.orders_tree.heading("created_at", text="Время создания")

        self.orders_tree.column("id", width=70)
        self.orders_tree.column("guest_name", width=150)
        self.orders_tree.column("table_number", width=60)
        self.orders_tree.column("total_amount", width=100)
        self.orders_tree.column("status", width=100)
        self.orders_tree.column("created_at", width=150)

        scrollbar = ttk.Scrollbar(self.orders_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления заказами
        button_frame = ttk.Frame(self.orders_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Готово", command=self.mark_ready).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Выдан", command=self.mark_delivered).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Печать чека", command=self.print_receipt).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.refresh_orders).pack(side="left", padx=5)

        # Фильтры
        filter_frame = ttk.Frame(self.orders_frame)
        filter_frame.pack(pady=5)

        ttk.Button(filter_frame, text="Все заказы", command=lambda: self.refresh_orders()).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="В обработке", command=lambda: self.refresh_orders("pending")).pack(side="left",
                                                                                                          padx=5)
        ttk.Button(filter_frame, text="Готовятся", command=lambda: self.refresh_orders("preparing")).pack(side="left",
                                                                                                          padx=5)
        ttk.Button(filter_frame, text="Готовые", command=lambda: self.refresh_orders("ready")).pack(side="left", padx=5)

        self.refresh_orders()

        # Привязка события выбора
        self.orders_tree.bind('<<TreeviewSelect>>', self.on_order_select)

    def setup_create_order(self):
        # Фрейм для информации о заказе
        info_frame = ttk.LabelFrame(self.create_order_frame, text="Информация о заказе")
        info_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(info_frame, text="Имя гостя:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
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
        self.category_combo = ttk.Combobox(category_frame, width=20)
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self.filter_menu_by_category)

        # Таблица меню
        columns = ("id", "name", "price", "category")
        self.menu_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)

        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Название")
        self.menu_tree.heading("price", text="Цена")
        self.menu_tree.heading("category", text="Категория")

        self.menu_tree.column("id", width=50)
        self.menu_tree.column("name", width=200)
        self.menu_tree.column("price", width=80)
        self.menu_tree.column("category", width=100)

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=scrollbar.set)

        self.menu_tree.pack(side="left", fill="both", expand=True)
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

        # Инициализация
        self.load_categories()
        self.refresh_menu()
        self.cart_items = []

    def load_categories(self):
        categories = db.get_menu_categories()
        category_list = [cat['category'] for cat in categories]
        self.category_combo['values'] = ['Все'] + category_list
        self.category_combo.set('Все')

    def filter_menu_by_category(self, event=None):
        self.refresh_menu()

    def refresh_menu(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        category = self.category_combo.get()
        if category == 'Все':
            menu_items = db.get_menu()
        else:
            menu_items = db.get_menu(category)

        for item in menu_items:
            self.menu_tree.insert("", "end", values=(
                item['id'], item['name'], f"{item['price']:.2f}", item['category']
            ))

    def add_to_cart(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо")
            return

        item = self.menu_tree.item(selected[0])['values']

        # Проверяем, есть ли уже это блюдо в корзине
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

        # Отображаем итоговую сумму
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
            messagebox.showwarning("Предупреждение", "Введите имя гостя")
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
            messagebox.showinfo("Успех", f"Заказ №{order_id} создан")
            self.clear_create_order_form()
            self.refresh_orders()
            self.notebook.select(self.orders_frame)
        else:
            messagebox.showerror("Ошибка", "Не удалось создать заказ")

    def clear_create_order_form(self):
        self.guest_name_entry.delete(0, tk.END)
        self.table_number_entry.delete(0, tk.END)
        self.cart_items = []
        self.update_cart_display()

    def refresh_orders(self, status=None):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        orders = db.get_all_orders(status)
        for order in orders:
            status_text = self.get_status_text(order['status'])
            self.orders_tree.insert("", "end", values=(
                order['id'], order['guest_name'], order['table_number'],
                f"{order['total_amount']:.2f}", status_text,
                order['created_at']
            ))

    def get_status_text(self, status):
        statuses = {
            'pending': 'В обработке',
            'preparing': 'Готовится',
            'ready': 'Готов',
            'delivered': 'Выдан',
            'cancelled': 'Отменен'
        }
        return statuses.get(status, status)

    def on_order_select(self, event):
        selected = self.orders_tree.selection()
        if selected:
            item = self.orders_tree.item(selected[0])['values']
            self.current_order_id = item[0]

    def mark_ready(self):
        if hasattr(self, 'current_order_id'):
            order = db.get_order_details(self.current_order_id)
            if order and order[0]['status'] == 'preparing':
                db.update_order_status(self.current_order_id, 'ready')
                messagebox.showinfo("Успех", "Заказ отмечен как готовый")
                self.refresh_orders()
            else:
                messagebox.showwarning("Предупреждение", "Заказ не в статусе 'Готовится'")
        else:
            messagebox.showwarning("Предупреждение", "Выберите заказ")

    def mark_delivered(self):
        if hasattr(self, 'current_order_id'):
            order = db.get_order_details(self.current_order_id)
            if order and order[0]['status'] == 'ready':
                db.update_order_status(self.current_order_id, 'delivered')
                messagebox.showinfo("Успех", "Заказ выдан")
                self.refresh_orders()
            else:
                messagebox.showwarning("Предупреждение", "Заказ не в статусе 'Готов'")
        else:
            messagebox.showwarning("Предупреждение", "Выберите заказ")

    def print_receipt(self):
        if hasattr(self, 'current_order_id'):
            receipt = db.generate_receipt(self.current_order_id)
            if receipt:
                self.show_receipt(receipt)
            else:
                messagebox.showerror("Ошибка", "Не удалось сформировать чек")
        else:
            messagebox.showwarning("Предупреждение", "Выберите заказ")

    def show_receipt(self, receipt):
        receipt_window = tk.Toplevel(self.window)
        receipt_window.title(f"Чек №{receipt['order_id']}")
        receipt_window.geometry("400x500")

        receipt_text = scrolledtext.ScrolledText(receipt_window, width=50, height=25)
        receipt_text.pack(padx=10, pady=10)

        receipt_content = f"""
        ╔════════════════════════════════════════╗
        ║              КАССОВЫЙ ЧЕК              ║
        ╠════════════════════════════════════════╣
        ║ Заказ №: {receipt['order_id']}
        ║ Гость: {receipt['guest_name']}
        ║ Стол: {receipt['table_number'] or 'Не указан'}
        ║ Время: {receipt['created_at']}
        ╠════════════════════════════════════════╣
        ║           Позиции заказа:             ║
        """

        for item in receipt['items']:
            receipt_content += f"""
        ║ {item['name']:<30}
        ║   {item['quantity']} x {item['price']:.2f} = {item['subtotal']:.2f} руб.
        """

        receipt_content += f"""
        ╠════════════════════════════════════════╣
        ║ ИТОГО К ОПЛАТЕ: {receipt['total_amount']:.2f} руб.
        ╚════════════════════════════════════════╝

        Спасибо за посещение!
        Ждем вас снова!
        """

        receipt_text.insert(1.0, receipt_content)
        receipt_text.config(state="disabled")

        ttk.Button(receipt_window, text="Закрыть", command=receipt_window.destroy).pack(pady=10)

    def logout(self):
        self.window.destroy()
        self.app.logout()