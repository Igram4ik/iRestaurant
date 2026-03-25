import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import db
from datetime import datetime, timedelta


class AdminWindow:
    def __init__(self, app, user):
        self.app = app
        self.user = user

        self.window = tk.Toplevel(app.root)
        self.window.title(f"Панель администратора - {user['username']}")
        self.window.geometry("1000x700")

        self.setup_menu()
        self.setup_ui()

    def setup_menu(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выйти", command=self.logout)

        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=reports_menu)
        reports_menu.add_command(label="Анализ выручки", command=self.show_revenue_analysis)

    def setup_ui(self):
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка управления меню
        self.menu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.menu_frame, text="Управление меню")
        self.setup_menu_management()

        # Вкладка просмотра заказов
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Все заказы")
        self.setup_orders_view()

        # Вкладка анализа выручки
        self.revenue_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.revenue_frame, text="Анализ выручки")
        self.setup_revenue_view()

    def setup_menu_management(self):
        # Панель для ввода данных
        input_frame = ttk.LabelFrame(self.menu_frame, text="Добавить/Редактировать блюдо")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        fields_frame = ttk.Frame(input_frame)
        fields_frame.pack(padx=10, pady=10)

        ttk.Label(fields_frame, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(fields_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=2, padx=5)

        ttk.Label(fields_frame, text="Описание:").grid(row=1, column=0, sticky="w", pady=2)
        self.desc_entry = ttk.Entry(fields_frame, width=30)
        self.desc_entry.grid(row=1, column=1, pady=2, padx=5)

        ttk.Label(fields_frame, text="Цена:").grid(row=2, column=0, sticky="w", pady=2)
        self.price_entry = ttk.Entry(fields_frame, width=30)
        self.price_entry.grid(row=2, column=1, pady=2, padx=5)

        ttk.Label(fields_frame, text="Категория:").grid(row=3, column=0, sticky="w", pady=2)
        self.category_entry = ttk.Entry(fields_frame, width=30)
        self.category_entry.grid(row=3, column=1, pady=2, padx=5)

        ttk.Label(fields_frame, text="Доступно:").grid(row=4, column=0, sticky="w", pady=2)
        self.available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(fields_frame, variable=self.available_var).grid(row=4, column=1, sticky="w", pady=2, padx=5)

        # Кнопки
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Добавить", command=self.add_menu_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.update_menu_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_menu_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_menu_form).pack(side="left", padx=5)

        # Список меню
        list_frame = ttk.LabelFrame(self.menu_frame, text="Список блюд")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица меню
        columns = ("id", "name", "description", "price", "category", "is_available")
        self.menu_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Название")
        self.menu_tree.heading("description", text="Описание")
        self.menu_tree.heading("price", text="Цена")
        self.menu_tree.heading("category", text="Категория")
        self.menu_tree.heading("is_available", text="Доступно")

        self.menu_tree.column("id", width=50)
        self.menu_tree.column("name", width=150)
        self.menu_tree.column("description", width=200)
        self.menu_tree.column("price", width=80)
        self.menu_tree.column("category", width=100)
        self.menu_tree.column("is_available", width=80)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=scrollbar.set)

        self.menu_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.menu_tree.bind('<<TreeviewSelect>>', self.on_menu_select)

        self.refresh_menu_list()

    def setup_orders_view(self):
        # Таблица заказов
        columns = ("id", "guest_name", "table_number", "total_amount", "status", "created_at", "items_count")
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=columns, show="headings", height=20)

        self.orders_tree.heading("id", text="№ заказа")
        self.orders_tree.heading("guest_name", text="Имя гостя")
        self.orders_tree.heading("table_number", text="Стол")
        self.orders_tree.heading("total_amount", text="Сумма")
        self.orders_tree.heading("status", text="Статус")
        self.orders_tree.heading("created_at", text="Время создания")
        self.orders_tree.heading("items_count", text="Кол-во позиций")

        self.orders_tree.column("id", width=70)
        self.orders_tree.column("guest_name", width=150)
        self.orders_tree.column("table_number", width=60)
        self.orders_tree.column("total_amount", width=100)
        self.orders_tree.column("status", width=100)
        self.orders_tree.column("created_at", width=150)
        self.orders_tree.column("items_count", width=100)

        scrollbar = ttk.Scrollbar(self.orders_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Кнопки фильтрации
        filter_frame = ttk.Frame(self.orders_frame)
        filter_frame.pack(pady=5)

        ttk.Button(filter_frame, text="Все заказы", command=lambda: self.refresh_orders()).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Активные заказы", command=lambda: self.refresh_orders("pending")).pack(
            side="left", padx=5)
        ttk.Button(filter_frame, text="Готовые заказы", command=lambda: self.refresh_orders("ready")).pack(side="left",
                                                                                                           padx=5)
        ttk.Button(filter_frame, text="Выполненные", command=lambda: self.refresh_orders("delivered")).pack(side="left",
                                                                                                            padx=5)

        self.refresh_orders()

    def setup_revenue_view(self):
        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.revenue_frame, text="Фильтры")
        filter_frame.pack(fill="x", padx=10, pady=5)

        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="Дата от:").pack(side="left", padx=5)
        self.date_from_entry = ttk.Entry(date_frame, width=15)
        self.date_from_entry.pack(side="left", padx=5)

        ttk.Label(date_frame, text="Дата до:").pack(side="left", padx=5)
        self.date_to_entry = ttk.Entry(date_frame, width=15)
        self.date_to_entry.pack(side="left", padx=5)

        ttk.Button(date_frame, text="Показать", command=self.update_revenue_report).pack(side="left", padx=10)

        # Текстовое поле для отчета
        self.report_text = scrolledtext.ScrolledText(self.revenue_frame, height=20)
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_revenue_report()

    def refresh_menu_list(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        menu_items = db.get_all_menu_items()
        for item in menu_items:
            self.menu_tree.insert("", "end", values=(
                item['id'], item['name'], item['description'],
                f"{item['price']:.2f}", item['category'],
                "Да" if item['is_available'] else "Нет"
            ))

    def refresh_orders(self, status=None):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        orders = db.get_all_orders(status)
        for order in orders:
            status_text = self.get_status_text(order['status'])
            self.orders_tree.insert("", "end", values=(
                order['id'], order['guest_name'], order['table_number'],
                f"{order['total_amount']:.2f}", status_text,
                order['created_at'], order['items_count']
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

    def add_menu_item(self):
        name = self.name_entry.get()
        description = self.desc_entry.get()
        price = self.price_entry.get()
        category = self.category_entry.get()

        if not all([name, price, category]):
            messagebox.showwarning("Предупреждение", "Заполните все обязательные поля")
            return

        try:
            price = float(price)
            db.add_menu_item(name, description, price, category)
            self.refresh_menu_list()
            self.clear_menu_form()
            messagebox.showinfo("Успех", "Блюдо добавлено")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная цена")

    def update_menu_item(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо для обновления")
            return

        item = self.menu_tree.item(selected[0])['values']
        item_id = item[0]

        name = self.name_entry.get()
        description = self.desc_entry.get()
        price = self.price_entry.get()
        category = self.category_entry.get()
        is_available = self.available_var.get()

        if not all([name, price, category]):
            messagebox.showwarning("Предупреждение", "Заполните все обязательные поля")
            return

        try:
            price = float(price)
            db.update_menu_item(item_id, name, description, price, category, is_available)
            self.refresh_menu_list()
            self.clear_menu_form()
            messagebox.showinfo("Успех", "Блюдо обновлено")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная цена")

    def delete_menu_item(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это блюдо?"):
            item = self.menu_tree.item(selected[0])['values']
            item_id = item[0]
            db.delete_menu_item(item_id)
            self.refresh_menu_list()
            self.clear_menu_form()
            messagebox.showinfo("Успех", "Блюдо удалено")

    def on_menu_select(self, event):
        selected = self.menu_tree.selection()
        if selected:
            item = self.menu_tree.item(selected[0])['values']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, item[1])
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, item[2])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, item[3])
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, item[4])
            self.available_var.set(item[5] == "Да")

    def clear_menu_form(self):
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.available_var.set(True)

    def update_revenue_report(self):
        date_from = self.date_from_entry.get()
        date_to = self.date_to_entry.get()

        if date_from and date_to:
            try:
                # Проверка формата даты
                datetime.strptime(date_from, '%Y-%m-%d')
                datetime.strptime(date_to, '%Y-%m-%d')
                revenue_data = db.get_revenue_analysis(date_from, date_to)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте YYYY-MM-DD")
                return
        else:
            revenue_data = db.get_revenue_analysis()

        self.report_text.delete(1.0, tk.END)

        if not revenue_data:
            self.report_text.insert(tk.END, "Нет данных о выручке за выбранный период")
            return

        total_revenue = sum(day['total_revenue'] for day in revenue_data)
        total_orders = sum(day['orders_count'] for day in revenue_data)
        avg_revenue = total_revenue / len(revenue_data) if revenue_data else 0

        report = f"""
        ╔════════════════════════════════════════════════════════════╗
        ║                    АНАЛИЗ ВЫРУЧКИ                         ║
        ╚════════════════════════════════════════════════════════════╝

        Общая выручка: {total_revenue:.2f} руб.
        Количество заказов: {total_orders}
        Средняя выручка в день: {avg_revenue:.2f} руб.

        ┌────────────────────────────────────────────────────────────┐
        │                    ДЕТАЛИЗАЦИЯ ПО ДНЯМ                    │
        └────────────────────────────────────────────────────────────┘

        """

        for day in revenue_data:
            report += f"""
        Дата: {day['date']}
        ├─ Заказов: {day['orders_count']}
        ├─ Выручка: {day['total_revenue']:.2f} руб.
        └─ Средний чек: {day['avg_order_value']:.2f} руб.

        """

        self.report_text.insert(tk.END, report)

    def show_revenue_analysis(self):
        self.notebook.select(self.revenue_frame)
        self.update_revenue_report()

    def logout(self):
        self.window.destroy()
        self.app.logout()