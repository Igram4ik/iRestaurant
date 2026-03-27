import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime, timedelta
import hashlib
import csv
import os
from decimal import Decimal, ROUND_HALF_UP


class DatabaseManager:
    """Класс для управления базой данных"""

    def __init__(self, db_name='restaurant.db'):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        """Получение соединения с БД"""
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Инициализация структуры базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                full_name VARCHAR(100)
            )
        ''')

        # Таблица категорий меню
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL
            )
        ''')

        # Таблица блюд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                category_id INTEGER,
                price DECIMAL(10, 2) NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES menu_categories(id)
            )
        ''')

        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_date DATETIME NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                cashier_id INTEGER,
                status VARCHAR(20) DEFAULT 'completed',
                table_number INTEGER,
                FOREIGN KEY (cashier_id) REFERENCES users(id)
            )
        ''')

        # Таблица позиций заказа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                menu_item_id INTEGER,
                quantity INTEGER NOT NULL,
                price_at_time DECIMAL(10, 2) NOT NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
            )
        ''')

        # Добавление тестовых данных
        self.insert_test_data(cursor)

        conn.commit()
        conn.close()

    def insert_test_data(self, cursor):
        """Вставка тестовых данных"""
        # Проверяем, есть ли уже пользователи
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Создание администратора (пароль: admin123)
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                ("admin", admin_hash, "admin", "Администратор")
            )

            # Создание кассира (пароль: cashier123)
            cashier_hash = hashlib.sha256("cashier123".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                ("cashier", cashier_hash, "cashier", "Кассир Иванов И.И.")
            )

        # Проверяем категории
        cursor.execute("SELECT COUNT(*) FROM menu_categories")
        if cursor.fetchone()[0] == 0:
            categories = [
                "Салаты", "Горячие блюда", "Напитки",
                "Десерты", "Закуски", "Супы"
            ]
            for cat in categories:
                cursor.execute("INSERT INTO menu_categories (name) VALUES (?)", (cat,))

        # Проверяем блюда
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] == 0:
            dishes = [
                (1, "Цезарь с курицей", 1, 350.00, 1, "Классический салат Цезарь с курицей"),
                (1, "Греческий салат", 1, 280.00, 1, "Салат с фетой и оливками"),
                (2, "Стейк Рибай", 2, 1200.00, 1, "Мраморная говядина"),
                (2, "Паста Карбонара", 2, 450.00, 1, "Спагетти с беконом в сливочном соусе"),
                (3, "Свежевыжатый апельсиновый сок", 3, 180.00, 1, "100% натуральный сок"),
                (3, "Капучино", 3, 150.00, 1, "Кофе с молоком"),
                (4, "Тирамису", 4, 320.00, 1, "Классический итальянский десерт"),
                (4, "Чизкейк", 4, 290.00, 1, "Нежный чизкейк с ягодным соусом"),
                (5, "Брускетта с томатами", 5, 220.00, 1, "Хрустящий хлеб с томатами и базиликом"),
                (6, "Суп-пюре из тыквы", 6, 260.00, 1, "Нежный суп с тыквенными семечками")
            ]
            for dish in dishes:
                cursor.execute(
                    "INSERT INTO menu_items (name, category_id, price, is_available, description) VALUES (?, ?, ?, ?, ?)",
                    (dish[0], dish[1], dish[2], dish[3], dish[4])
                )

    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, full_name FROM users WHERE username=? AND password_hash=?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()
        return user

    def get_categories(self):
        """Получение списка категорий"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM menu_categories ORDER BY name")
        categories = cursor.fetchall()
        conn.close()
        return categories

    def get_menu_items(self, category_id=None):
        """Получение блюд меню"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if category_id:
            cursor.execute(
                "SELECT id, name, price, is_available, description FROM menu_items WHERE category_id=? AND is_available=1 ORDER BY name",
                (category_id,)
            )
        else:
            cursor.execute(
                "SELECT id, name, price, is_available, description FROM menu_items WHERE is_available=1 ORDER BY name"
            )
        items = cursor.fetchall()
        conn.close()
        return items

    def create_order(self, cashier_id, items, table_number=None):
        """Создание нового заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Рассчитываем общую сумму
            total_amount = sum(item['subtotal'] for item in items)

            # Создаем заказ
            cursor.execute(
                "INSERT INTO orders (order_date, total_amount, cashier_id, status, table_number) VALUES (?, ?, ?, ?, ?)",
                (datetime.now(), total_amount, cashier_id, 'completed', table_number)
            )
            order_id = cursor.lastrowid

            # Добавляем позиции заказа
            for item in items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, menu_item_id, quantity, price_at_time, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (order_id, item['menu_item_id'], item['quantity'], item['price'], item['subtotal'])
                )

            conn.commit()
            return order_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_orders(self, start_date=None, end_date=None):
        """Получение списка заказов за период"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT o.id, o.order_date, o.total_amount, u.full_name, o.table_number
            FROM orders o
            LEFT JOIN users u ON o.cashier_id = u.id
            WHERE o.status = 'completed'
        """
        params = []

        if start_date:
            query += " AND o.order_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND o.order_date <= ?"
            params.append(end_date)

        query += " ORDER BY o.order_date DESC"

        cursor.execute(query, params)
        orders = cursor.fetchall()
        conn.close()
        return orders

    def get_order_details(self, order_id):
        """Получение деталей заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT oi.id, mi.name, oi.quantity, oi.price_at_time, oi.subtotal
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE oi.order_id = ?
        """, (order_id,))

        items = cursor.fetchall()
        conn.close()
        return items

    def get_sales_report(self, start_date, end_date):
        """Получение отчета о продажах"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Основная статистика
        cursor.execute("""
            SELECT 
                COUNT(*) as order_count,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_check
            FROM orders
            WHERE status = 'completed'
                AND order_date >= ?
                AND order_date <= ?
        """, (start_date, end_date))

        stats = cursor.fetchone()

        # Топ-5 популярных блюд
        cursor.execute("""
            SELECT mi.name, SUM(oi.quantity) as total_quantity
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE o.status = 'completed'
                AND o.order_date >= ?
                AND o.order_date <= ?
            GROUP BY mi.name
            ORDER BY total_quantity DESC
            LIMIT 5
        """, (start_date, end_date))

        top_dishes = cursor.fetchall()

        # Выручка по категориям
        cursor.execute("""
            SELECT mc.name, SUM(oi.subtotal) as revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            JOIN menu_categories mc ON mi.category_id = mc.id
            WHERE o.status = 'completed'
                AND o.order_date >= ?
                AND o.order_date <= ?
            GROUP BY mc.name
            ORDER BY revenue DESC
        """, (start_date, end_date))

        category_revenue = cursor.fetchall()

        conn.close()

        return {
            'order_count': stats[0] or 0,
            'total_revenue': stats[1] or 0,
            'avg_check': stats[2] or 0,
            'top_dishes': top_dishes,
            'category_revenue': category_revenue
        }

    def get_all_menu_items_for_admin(self):
        """Получение всех блюд для администрирования"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mi.id, mi.name, mc.name as category, mi.price, mi.is_available, mi.description
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.id
            ORDER BY mc.name, mi.name
        """)
        items = cursor.fetchall()
        conn.close()
        return items

    def add_menu_item(self, name, category_id, price, description):
        """Добавление нового блюда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu_items (name, category_id, price, description, is_available) VALUES (?, ?, ?, ?, 1)",
            (name, category_id, price, description)
        )
        conn.commit()
        conn.close()

    def update_menu_item(self, item_id, name, category_id, price, is_available, description):
        """Обновление блюда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE menu_items 
            SET name=?, category_id=?, price=?, is_available=?, description=?
            WHERE id=?
        """, (name, category_id, price, is_available, description, item_id))
        conn.commit()
        conn.close()

    def delete_menu_item(self, item_id):
        """Удаление блюда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()


class LoginWindow:
    """Окно авторизации"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("АИС Ресторан - Авторизация")
        self.window.geometry("400x350")
        self.window.resizable(False, False)

        self.db = DatabaseManager()
        self.current_user = None

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        title_label = tk.Label(self.window, text="АИС Ресторан",
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        # Форма входа
        login_frame = tk.Frame(self.window)
        login_frame.pack(pady=20)

        tk.Label(login_frame, text="Логин:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=20)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(login_frame, text="Пароль:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12), width=20)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Вход", command=self.login,
                  font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Выход", command=self.window.quit,
                  font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=5)

        # Информация
        info_label = tk.Label(self.window,
                              text="Тестовые учетные записи:\nАдмин: admin / admin123\nКассир: cashier / cashier123",
                              font=("Arial", 9), fg="gray")
        info_label.pack(side=tk.BOTTOM, pady=10)

        self.window.bind('<Return>', lambda e: self.login())

    def login(self):
        """Обработка входа"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        user = self.db.authenticate_user(username, password)

        if user:
            self.current_user = user
            self.window.destroy()
            self.open_main_window()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def open_main_window(self):
        """Открытие главного окна"""
        if self.current_user[2] == 'admin':
            app = AdminApp(self.db, self.current_user)
        else:
            app = CashierApp(self.db, self.current_user)
        app.run()

    def run(self):
        """Запуск окна авторизации"""
        self.window.mainloop()


class CashierApp:
    """Приложение для кассира"""

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.window = tk.Tk()
        self.window.title(f"АИС Ресторан - Касса (Кассир: {user[3]})")
        self.window.geometry("1200x700")

        self.cart = []  # Корзина заказов
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса кассира"""
        # Основной контейнер
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - меню
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Заголовок меню
        tk.Label(left_frame, text="Меню", font=("Arial", 16, "bold")).pack(pady=5)

        # Категории
        categories_frame = tk.Frame(left_frame)
        categories_frame.pack(fill=tk.X, pady=5)

        self.category_buttons = {}
        categories = self.db.get_categories()

        for cat in categories:
            btn = tk.Button(categories_frame, text=cat[1],
                            command=lambda cid=cat[0]: self.load_menu_items(cid),
                            font=("Arial", 10))
            btn.pack(side=tk.LEFT, padx=2)
            self.category_buttons[cat[0]] = btn

        # Таблица блюд
        self.menu_tree = ttk.Treeview(left_frame, columns=("id", "name", "price"),
                                      show="headings", height=20)
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Блюдо")
        self.menu_tree.heading("price", text="Цена")
        self.menu_tree.column("id", width=50)
        self.menu_tree.column("name", width=300)
        self.menu_tree.column("price", width=100)
        self.menu_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопка добавления в корзину
        tk.Button(left_frame, text="Добавить в заказ", command=self.add_to_cart,
                  font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=5)

        # Правая панель - корзина
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Заголовок корзины
        tk.Label(right_frame, text="Текущий заказ", font=("Arial", 16, "bold")).pack(pady=5)

        # Номер стола
        table_frame = tk.Frame(right_frame)
        table_frame.pack(fill=tk.X, pady=5)
        tk.Label(table_frame, text="Номер стола:").pack(side=tk.LEFT, padx=5)
        self.table_entry = tk.Entry(table_frame, width=10)
        self.table_entry.pack(side=tk.LEFT, padx=5)

        # Таблица корзины
        self.cart_tree = ttk.Treeview(right_frame, columns=("name", "quantity", "price", "subtotal"),
                                      show="headings", height=15)
        self.cart_tree.heading("name", text="Блюдо")
        self.cart_tree.heading("quantity", text="Кол-во")
        self.cart_tree.heading("price", text="Цена")
        self.cart_tree.heading("subtotal", text="Сумма")
        self.cart_tree.column("name", width=200)
        self.cart_tree.column("quantity", width=80)
        self.cart_tree.column("price", width=100)
        self.cart_tree.column("subtotal", width=100)
        self.cart_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопки управления корзиной
        cart_buttons_frame = tk.Frame(right_frame)
        cart_buttons_frame.pack(fill=tk.X, pady=5)

        tk.Button(cart_buttons_frame, text="Удалить позицию", command=self.remove_from_cart,
                  bg="#f44336", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(cart_buttons_frame, text="Изменить количество", command=self.change_quantity,
                  bg="#ff9800", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(cart_buttons_frame, text="Очистить корзину", command=self.clear_cart,
                  bg="#9E9E9E", fg="white").pack(side=tk.LEFT, padx=2)

        # Итоговая панель
        total_frame = tk.Frame(right_frame)
        total_frame.pack(fill=tk.X, pady=10)

        self.total_label = tk.Label(total_frame, text="Итого: 0.00 руб.",
                                    font=("Arial", 14, "bold"))
        self.total_label.pack(side=tk.LEFT)

        tk.Button(total_frame, text="Оформить заказ", command=self.create_order,
                  font=("Arial", 12), bg="#2196F3", fg="white").pack(side=tk.RIGHT, padx=5)
        tk.Button(total_frame, text="Отмена", command=self.clear_cart,
                  font=("Arial", 12), bg="#9E9E9E", fg="white").pack(side=tk.RIGHT, padx=5)

        # Загрузка всех блюд
        self.load_menu_items()

    def load_menu_items(self, category_id=None):
        """Загрузка блюд меню"""
        # Очистка таблицы
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        # Загрузка блюд
        items = self.db.get_menu_items(category_id)
        for item in items:
            self.menu_tree.insert("", tk.END, values=(item[0], item[1], f"{item[2]:.2f}"))

    def add_to_cart(self):
        """Добавление блюда в корзину"""
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо из меню")
            return

        item = self.menu_tree.item(selected[0])
        item_id = item['values'][0]
        item_name = item['values'][1]
        item_price = float(item['values'][2])

        # Запрос количества
        quantity = self.get_quantity()
        if quantity is None or quantity <= 0:
            return

        # Проверяем, есть ли уже такое блюдо в корзине
        for i, cart_item in enumerate(self.cart):
            if cart_item['menu_item_id'] == item_id:
                # Обновляем количество
                self.cart[i]['quantity'] += quantity
                self.cart[i]['subtotal'] = self.cart[i]['quantity'] * self.cart[i]['price']
                self.update_cart_display()
                self.update_total()
                return

        # Добавляем новое блюдо
        self.cart.append({
            'menu_item_id': item_id,
            'name': item_name,
            'quantity': quantity,
            'price': item_price,
            'subtotal': quantity * item_price
        })

        self.update_cart_display()
        self.update_total()

    def get_quantity(self):
        """Запрос количества"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Количество")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="Введите количество:", font=("Arial", 12)).pack(pady=10)
        quantity_entry = tk.Entry(dialog, font=("Arial", 12))
        quantity_entry.pack(pady=5)

        result = [None]

        def confirm():
            try:
                qty = int(quantity_entry.get())
                if qty > 0:
                    result[0] = qty
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Количество должно быть больше 0")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")

        tk.Button(dialog, text="OK", command=confirm).pack(pady=10)

        dialog.wait_window()
        return result[0]

    def update_cart_display(self):
        """Обновление отображения корзины"""
        # Очистка таблицы
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        # Добавление позиций
        for item in self.cart:
            self.cart_tree.insert("", tk.END, values=(
                item['name'],
                item['quantity'],
                f"{item['price']:.2f}",
                f"{item['subtotal']:.2f}"
            ))

    def remove_from_cart(self):
        """Удаление позиции из корзины"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите позицию для удаления")
            return

        index = self.cart_tree.index(selected[0])
        del self.cart[index]

        self.update_cart_display()
        self.update_total()

    def change_quantity(self):
        """Изменение количества"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите позицию")
            return

        index = self.cart_tree.index(selected[0])
        current_item = self.cart[index]

        new_quantity = self.get_quantity()
        if new_quantity and new_quantity > 0:
            self.cart[index]['quantity'] = new_quantity
            self.cart[index]['subtotal'] = new_quantity * self.cart[index]['price']
            self.update_cart_display()
            self.update_total()

    def clear_cart(self):
        """Очистка корзины"""
        if self.cart and messagebox.askyesno("Подтверждение", "Очистить корзину?"):
            self.cart = []
            self.update_cart_display()
            self.update_total()

    def update_total(self):
        """Обновление итоговой суммы"""
        total = sum(item['subtotal'] for item in self.cart)
        self.total_label.config(text=f"Итого: {total:.2f} руб.")

    def create_order(self):
        """Создание заказа"""
        if not self.cart:
            messagebox.showwarning("Предупреждение", "Корзина пуста")
            return

        table_number = self.table_entry.get()
        if not table_number:
            table_number = None
        else:
            try:
                table_number = int(table_number)
            except ValueError:
                messagebox.showerror("Ошибка", "Номер стола должен быть числом")
                return

        # Создание заказа
        try:
            order_id = self.db.create_order(self.user[0], self.cart, table_number)

            # Показ чека
            self.show_receipt(order_id)

            # Очистка корзины
            self.clear_cart()

            messagebox.showinfo("Успех", f"Заказ №{order_id} успешно оформлен!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при оформлении заказа: {str(e)}")

    def show_receipt(self, order_id):
        """Показ чека"""
        receipt_window = tk.Toplevel(self.window)
        receipt_window.title(f"Чек №{order_id}")
        receipt_window.geometry("500x600")

        # Получение деталей заказа
        order_details = self.db.get_order_details(order_id)

        # Создание текста чека
        receipt_text = scrolledtext.ScrolledText(receipt_window, font=("Courier", 10))
        receipt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Формирование чека
        receipt_content = f"""
{"=" * 40}
        АИС РЕСТОРАН
        ЧЕК №{order_id}
{"=" * 40}
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Кассир: {self.user[3]}
Номер стола: {self.table_entry.get() or 'Без стола'}
{"=" * 40}
Наименование     Кол-во   Цена    Сумма
{"-" * 40}
"""

        for item in order_details:
            receipt_content += f"{item[1]:<15} {item[2]:>3}   {item[3]:>6.2f} {item[4]:>8.2f}\n"

        receipt_content += f"""
{"=" * 40}
ИТОГО: {sum(item[4] for item in order_details):.2f} руб.
{"=" * 40}

Спасибо за визит!
Приходите снова!
"""

        receipt_text.insert(1.0, receipt_content)
        receipt_text.config(state=tk.DISABLED)

        # Кнопка печати (сохранение в файл)
        def save_receipt():
            filename = f"receipt_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_content)
            messagebox.showinfo("Успех", f"Чек сохранен в файл: {filename}")

        tk.Button(receipt_window, text="Сохранить чек", command=save_receipt,
                  font=("Arial", 10)).pack(pady=5)

    def run(self):
        """Запуск приложения"""
        self.window.mainloop()


class AdminApp:
    """Приложение для администратора"""

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.window = tk.Tk()
        self.window.title(f"АИС Ресторан - Администрирование (Админ: {user[3]})")
        self.window.geometry("1200x700")

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса администратора"""
        # Создание вкладок
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка истории заказов
        self.history_frame = tk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="История заказов")
        self.setup_history_tab()

        # Вкладка отчетов
        self.reports_frame = tk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Отчеты о выручке")
        self.setup_reports_tab()

        # Вкладка управления меню
        self.menu_management_frame = tk.Frame(self.notebook)
        self.notebook.add(self.menu_management_frame, text="Управление меню")
        self.setup_menu_management_tab()

    def setup_history_tab(self):
        """Настройка вкладки истории заказов"""
        # Панель фильтров
        filter_frame = tk.Frame(self.history_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Дата от:").pack(side=tk.LEFT, padx=5)
        self.start_date_entry = tk.Entry(filter_frame, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        self.start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        tk.Label(filter_frame, text="Дата до:").pack(side=tk.LEFT, padx=5)
        self.end_date_entry = tk.Entry(filter_frame, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        tk.Button(filter_frame, text="Показать", command=self.load_orders,
                  bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Обновить", command=self.load_orders,
                  bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        # Таблица заказов
        columns = ("id", "date", "total", "cashier", "table")
        self.orders_tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=20)
        self.orders_tree.heading("id", text="№ заказа")
        self.orders_tree.heading("date", text="Дата/время")
        self.orders_tree.heading("total", text="Сумма")
        self.orders_tree.heading("cashier", text="Кассир")
        self.orders_tree.heading("table", text="Стол")
        self.orders_tree.column("id", width=80)
        self.orders_tree.column("date", width=150)
        self.orders_tree.column("total", width=100)
        self.orders_tree.column("cashier", width=150)
        self.orders_tree.column("table", width=80)
        self.orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопка просмотра деталей
        tk.Button(self.history_frame, text="Просмотреть детали заказа",
                  command=self.view_order_details,
                  font=("Arial", 12), bg="#FF9800", fg="white").pack(pady=5)

        # Загрузка заказов
        self.load_orders()

    def setup_reports_tab(self):
        """Настройка вкладки отчетов"""
        # Панель выбора периода
        period_frame = tk.Frame(self.reports_frame)
        period_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(period_frame, text="Период:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        self.period_var = tk.StringVar(value="today")
        periods = [
            ("Сегодня", "today"),
            ("Вчера", "yesterday"),
            ("Эта неделя", "this_week"),
            ("Этот месяц", "this_month"),
            ("Произвольный", "custom")
        ]

        for text, value in periods:
            tk.Radiobutton(period_frame, text=text, variable=self.period_var,
                           value=value, command=self.on_period_change).pack(side=tk.LEFT, padx=5)

        # Произвольный период
        self.custom_frame = tk.Frame(self.reports_frame)

        tk.Label(self.custom_frame, text="С:").pack(side=tk.LEFT, padx=5)
        self.custom_start = tk.Entry(self.custom_frame, width=12)
        self.custom_start.pack(side=tk.LEFT, padx=5)
        self.custom_start.insert(0, datetime.now().strftime('%Y-%m-%d'))

        tk.Label(self.custom_frame, text="По:").pack(side=tk.LEFT, padx=5)
        self.custom_end = tk.Entry(self.custom_frame, width=12)
        self.custom_end.pack(side=tk.LEFT, padx=5)
        self.custom_end.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Кнопка формирования отчета
        tk.Button(self.reports_frame, text="Сформировать отчет",
                  command=self.generate_report,
                  font=("Arial", 12), bg="#2196F3", fg="white").pack(pady=10)

        # Текстовое поле для отчета
        self.report_text = scrolledtext.ScrolledText(self.reports_frame, font=("Courier", 10), height=25)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопка экспорта
        tk.Button(self.reports_frame, text="Экспортировать отчет",
                  command=self.export_report,
                  font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=5)

    def setup_menu_management_tab(self):
        """Настройка вкладки управления меню"""
        # Таблица блюд
        columns = ("id", "name", "category", "price", "available", "description")
        self.menu_tree = ttk.Treeview(self.menu_management_frame, columns=columns, show="headings", height=20)
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Название")
        self.menu_tree.heading("category", text="Категория")
        self.menu_tree.heading("price", text="Цена")
        self.menu_tree.heading("available", text="Доступно")
        self.menu_tree.heading("description", text="Описание")
        self.menu_tree.column("id", width=50)
        self.menu_tree.column("name", width=150)
        self.menu_tree.column("category", width=100)
        self.menu_tree.column("price", width=80)
        self.menu_tree.column("available", width=80)
        self.menu_tree.column("description", width=300)
        self.menu_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопки управления
        button_frame = tk.Frame(self.menu_management_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(button_frame, text="Добавить блюдо", command=self.add_menu_item,
                  bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Редактировать", command=self.edit_menu_item,
                  bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Удалить", command=self.delete_menu_item,
                  bg="#f44336", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Обновить", command=self.load_menu_items,
                  bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=2)

        # Загрузка меню
        self.load_menu_items()

    def load_orders(self):
        """Загрузка заказов"""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        # Добавляем время к датам
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"

        orders = self.db.get_orders(start_datetime, end_datetime)

        # Очистка таблицы
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Заполнение таблицы
        for order in orders:
            self.orders_tree.insert("", tk.END, values=(
                order[0],
                order[1],
                f"{order[2]:.2f}",
                order[3],
                order[4] or "-"
            ))

    def view_order_details(self):
        """Просмотр деталей заказа"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return

        order_id = self.orders_tree.item(selected[0])['values'][0]

        details_window = tk.Toplevel(self.window)
        details_window.title(f"Детали заказа №{order_id}")
        details_window.geometry("600x400")

        # Получение деталей
        items = self.db.get_order_details(order_id)

        # Создание текстового поля
        text = scrolledtext.ScrolledText(details_window, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Формирование текста
        content = f"""
{"=" * 50}
ДЕТАЛИ ЗАКАЗА №{order_id}
{"=" * 50}

Наименование          Кол-во    Цена     Сумма
{"-" * 50}
"""
        for item in items:
            content += f"{item[1]:<20} {item[2]:>3}     {item[3]:>6.2f}  {item[4]:>8.2f}\n"

        content += f"""
{"=" * 50}
ИТОГО: {sum(item[4] for item in items):.2f} руб.
"""

        text.insert(1.0, content)
        text.config(state=tk.DISABLED)

    def on_period_change(self):
        """Обработка изменения периода"""
        if self.period_var.get() == "custom":
            self.custom_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.custom_frame.pack_forget()

    def generate_report(self):
        """Генерация отчета"""
        period = self.period_var.get()

        if period == "today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
        elif period == "yesterday":
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59)
        elif period == "this_week":
            start_date = datetime.now() - timedelta(days=datetime.now().weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
        elif period == "this_month":
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
        else:  # custom
            start_date = datetime.strptime(self.custom_start.get(), '%Y-%m-%d')
            end_date = datetime.strptime(self.custom_end.get(), '%Y-%m-%d')
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Получение отчета
        report = self.db.get_sales_report(start_date, end_date)

        # Формирование текста отчета
        report_content = f"""
{"=" * 60}
          ОТЧЕТ О ВЫРУЧКЕ
{"=" * 60}
Период: {start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')}
{"=" * 60}

ОСНОВНЫЕ ПОКАЗАТЕЛИ:
• Всего заказов: {report['order_count']}
• Общая выручка: {report['total_revenue']:.2f} руб.
• Средний чек: {report['avg_check']:.2f} руб.

{"=" * 60}
ТОП-5 ПОПУЛЯРНЫХ БЛЮД:
{"=" * 60}
"""

        for i, dish in enumerate(report['top_dishes'], 1):
            report_content += f"{i}. {dish[0]} - {dish[1]} шт.\n"

        report_content += f"""
{"=" * 60}
ВЫРУЧКА ПО КАТЕГОРИЯМ:
{"=" * 60}
"""

        for category, revenue in report['category_revenue']:
            report_content += f"{category}: {revenue:.2f} руб.\n"

        report_content += f"""
{"=" * 60}
"""

        # Отображение отчета
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report_content)

        # Сохраняем отчет для экспорта
        self.current_report = report_content

    def export_report(self):
        """Экспорт отчета"""
        if not hasattr(self, 'current_report'):
            messagebox.showwarning("Предупреждение", "Сначала сформируйте отчет")
            return

        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.current_report)

        messagebox.showinfo("Успех", f"Отчет сохранен в файл: {filename}")

    def load_menu_items(self):
        """Загрузка блюд для управления"""
        # Очистка таблицы
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        items = self.db.get_all_menu_items_for_admin()
        for item in items:
            self.menu_tree.insert("", tk.END, values=(
                item[0], item[1], item[2], f"{item[3]:.2f}",
                "Да" if item[4] else "Нет", item[5]
            ))

    def add_menu_item(self):
        """Добавление нового блюда"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавление блюда")
        dialog.geometry("500x400")
        dialog.transient(self.window)
        dialog.grab_set()

        # Поля ввода
        fields = {}
        labels = ["Название:", "Категория:", "Цена:", "Описание:"]

        for i, label in enumerate(labels):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if label == "Категория:":
                categories = self.db.get_categories()
                fields['category'] = ttk.Combobox(dialog, values=[cat[1] for cat in categories])
                fields['category'].grid(row=i, column=1, padx=5, pady=5, sticky="w")
            elif label == "Описание:":
                fields['description'] = tk.Text(dialog, height=5, width=30)
                fields['description'].grid(row=i, column=1, padx=5, pady=5, sticky="w")
            else:
                fields[label.lower()] = tk.Entry(dialog, width=30)
                fields[label.lower()].grid(row=i, column=1, padx=5, pady=5, sticky="w")

        def save_item():
            try:
                name = fields['название:'].get()
                category_name = fields['category'].get()
                price = float(fields['цена:'].get())
                description = fields['description'].get(1.0, tk.END).strip()

                if not name or not category_name:
                    messagebox.showerror("Ошибка", "Заполните обязательные поля")
                    return

                # Получаем ID категории
                categories = self.db.get_categories()
                category_id = None
                for cat in categories:
                    if cat[1] == category_name:
                        category_id = cat[0]
                        break

                if category_id is None:
                    messagebox.showerror("Ошибка", "Выберите категорию")
                    return

                self.db.add_menu_item(name, category_id, price, description)
                messagebox.showinfo("Успех", "Блюдо успешно добавлено")
                dialog.destroy()
                self.load_menu_items()

            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная цена")

        tk.Button(dialog, text="Сохранить", command=save_item,
                  bg="#4CAF50", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    def edit_menu_item(self):
        """Редактирование блюда"""
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо для редактирования")
            return

        item = self.menu_tree.item(selected[0])['values']
        item_id = item[0]

        dialog = tk.Toplevel(self.window)
        dialog.title("Редактирование блюда")
        dialog.geometry("500x450")
        dialog.transient(self.window)
        dialog.grab_set()

        # Поля ввода
        fields = {}
        labels = ["Название:", "Категория:", "Цена:", "Доступно:", "Описание:"]

        for i, label in enumerate(labels):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")

            if label == "Категория:":
                categories = self.db.get_categories()
                fields['category'] = ttk.Combobox(dialog, values=[cat[1] for cat in categories])
                fields['category'].grid(row=i, column=1, padx=5, pady=5, sticky="w")
                fields['category'].set(item[2])
            elif label == "Доступно:":
                fields['available'] = ttk.Combobox(dialog, values=["Да", "Нет"])
                fields['available'].grid(row=i, column=1, padx=5, pady=5, sticky="w")
                fields['available'].set(item[4])
            elif label == "Описание:":
                fields['description'] = tk.Text(dialog, height=5, width=30)
                fields['description'].grid(row=i, column=1, padx=5, pady=5, sticky="w")
                fields['description'].insert(1.0, item[5])
            else:
                fields[label.lower()] = tk.Entry(dialog, width=30)
                fields[label.lower()].grid(row=i, column=1, padx=5, pady=5, sticky="w")
                fields[label.lower()].insert(0, item[1] if label == "Название:" else item[3])

        def update_item():
            try:
                name = fields['название:'].get()
                category_name = fields['category'].get()
                price = float(fields['цена:'].get())
                is_available = 1 if fields['available'].get() == "Да" else 0
                description = fields['description'].get(1.0, tk.END).strip()

                if not name or not category_name:
                    messagebox.showerror("Ошибка", "Заполните обязательные поля")
                    return

                # Получаем ID категории
                categories = self.db.get_categories()
                category_id = None
                for cat in categories:
                    if cat[1] == category_name:
                        category_id = cat[0]
                        break

                if category_id is None:
                    messagebox.showerror("Ошибка", "Выберите категорию")
                    return

                self.db.update_menu_item(item_id, name, category_id, price, is_available, description)
                messagebox.showinfo("Успех", "Блюдо успешно обновлено")
                dialog.destroy()
                self.load_menu_items()

            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная цена")

        tk.Button(dialog, text="Обновить", command=update_item,
                  bg="#FF9800", fg="white").grid(row=5, column=0, columnspan=2, pady=10)

    def delete_menu_item(self):
        """Удаление блюда"""
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранное блюдо?"):
            item = self.menu_tree.item(selected[0])['values']
            item_id = item[0]
            self.db.delete_menu_item(item_id)
            messagebox.showinfo("Успех", "Блюдо удалено")
            self.load_menu_items()

    def run(self):
        """Запуск приложения"""
        self.window.mainloop()


# Запуск приложения
if __name__ == "__main__":
    app = LoginWindow()
    app.run()