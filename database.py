import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='direct.igrammine.ru:3838',
                database='iRestaurant',
                user='root',
                password='',  # Укажите ваш пароль
                autocommit=True
            )
            return True
        except Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None
        finally:
            cursor.close()

    # Методы для работы с пользователями
    def authenticate_user(self, username, password):
        query = "SELECT * FROM users WHERE username = %s"
        user = self.execute_query(query, (username,))
        if user and len(user) > 0:
            # В реальном приложении используйте хэширование паролей
            if user[0]['password'] == password:
                return user[0]
        return None

    # Методы для работы с меню
    def get_menu(self, category=None):
        if category:
            query = "SELECT * FROM menu WHERE is_available = TRUE AND category = %s ORDER BY category, name"
            return self.execute_query(query, (category,))
        else:
            query = "SELECT * FROM menu WHERE is_available = TRUE ORDER BY category, name"
            return self.execute_query(query)

    def get_all_menu_items(self):
        query = "SELECT * FROM menu ORDER BY category, name"
        return self.execute_query(query)

    def add_menu_item(self, name, description, price, category):
        query = """INSERT INTO menu (name, description, price, category) 
                   VALUES (%s, %s, %s, %s)"""
        return self.execute_query(query, (name, description, price, category))

    def update_menu_item(self, item_id, name, description, price, category, is_available):
        query = """UPDATE menu SET name=%s, description=%s, price=%s, 
                   category=%s, is_available=%s WHERE id=%s"""
        return self.execute_query(query, (name, description, price, category, is_available, item_id))

    def delete_menu_item(self, item_id):
        query = "DELETE FROM menu WHERE id=%s"
        return self.execute_query(query, (item_id,))

    def get_menu_categories(self):
        query = "SELECT DISTINCT category FROM menu WHERE is_available = TRUE ORDER BY category"
        return self.execute_query(query)

    # Методы для работы с заказами
    def create_order(self, guest_name, table_number, items):
        # Создаем заказ
        query = "INSERT INTO orders (guest_name, table_number) VALUES (%s, %s)"
        order_id = self.execute_query(query, (guest_name, table_number))

        if order_id:
            total = 0
            # Добавляем позиции заказа
            for item in items:
                query = """INSERT INTO order_items (order_id, menu_id, quantity, price) 
                           VALUES (%s, %s, %s, %s)"""
                self.execute_query(query, (order_id, item['menu_id'], item['quantity'], item['price']))
                total += item['price'] * item['quantity']

            # Обновляем общую сумму заказа
            query = "UPDATE orders SET total_amount = %s WHERE id = %s"
            self.execute_query(query, (total, order_id))

        return order_id

    def get_all_orders(self, status=None):
        if status:
            query = """SELECT o.*, 
                      (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as items_count
                      FROM orders o WHERE status = %s ORDER BY created_at DESC"""
            return self.execute_query(query, (status,))
        else:
            query = """SELECT o.*, 
                      (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as items_count
                      FROM orders o ORDER BY created_at DESC"""
            return self.execute_query(query)

    def get_order_details(self, order_id):
        query = """SELECT o.*, oi.id as item_id, oi.quantity, oi.price, m.name as item_name
                   FROM orders o
                   LEFT JOIN order_items oi ON o.id = oi.order_id
                   LEFT JOIN menu m ON oi.menu_id = m.id
                   WHERE o.id = %s"""
        return self.execute_query(query, (order_id,))

    def update_order_status(self, order_id, status):
        query = "UPDATE orders SET status = %s WHERE id = %s"
        return self.execute_query(query, (status, order_id))

    def get_revenue_analysis(self, date_from=None, date_to=None):
        if date_from and date_to:
            query = """SELECT DATE(created_at) as date, 
                              COUNT(*) as orders_count,
                              SUM(total_amount) as total_revenue,
                              AVG(total_amount) as avg_order_value
                       FROM orders 
                       WHERE status = 'delivered' 
                       AND DATE(created_at) BETWEEN %s AND %s
                       GROUP BY DATE(created_at)
                       ORDER BY date DESC"""
            return self.execute_query(query, (date_from, date_to))
        else:
            query = """SELECT DATE(created_at) as date, 
                              COUNT(*) as orders_count,
                              SUM(total_amount) as total_revenue,
                              AVG(total_amount) as avg_order_value
                       FROM orders 
                       WHERE status = 'delivered'
                       GROUP BY DATE(created_at)
                       ORDER BY date DESC
                       LIMIT 30"""
            return self.execute_query(query)

    def generate_receipt(self, order_id):
        order_details = self.get_order_details(order_id)
        if not order_details:
            return None

        receipt = {
            'order_id': order_details[0]['id'],
            'guest_name': order_details[0]['guest_name'],
            'table_number': order_details[0]['table_number'],
            'created_at': order_details[0]['created_at'],
            'total_amount': order_details[0]['total_amount'],
            'items': []
        }

        for item in order_details:
            if item['item_id']:
                receipt['items'].append({
                    'name': item['item_name'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'subtotal': item['quantity'] * item['price']
                })

        return receipt


db = Database()