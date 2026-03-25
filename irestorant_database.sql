-- Создание базы данных
CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'cashier', 'guest') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица меню
CREATE TABLE IF NOT EXISTS menu (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    guest_name VARCHAR(100),
    table_number INT,
    total_amount DECIMAL(10, 2),
    status ENUM('pending', 'preparing', 'ready', 'delivered', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Таблица деталей заказа
CREATE TABLE IF NOT EXISTS order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    menu_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES menu(id)
);

-- Вставка тестовых данных
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('cashier', 'cashier123', 'cashier');

INSERT INTO menu (name, description, price, category) VALUES
('Цезарь с курицей', 'Классический салат с курицей, сухариками и соусом Цезарь', 450.00, 'Салаты'),
('Стейк Рибай', 'Стейк из мраморной говядины с овощами гриль', 1200.00, 'Горячие блюда'),
('Спагетти Карбонара', 'Паста с беконом, сливочным соусом и пармезаном', 550.00, 'Паста'),
('Тирамису', 'Классический итальянский десерт', 350.00, 'Десерты');