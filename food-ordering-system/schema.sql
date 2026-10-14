CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

CREATE TABLE IF NOT EXISTS users (
  user_id   INT AUTO_INCREMENT PRIMARY KEY,
  username  VARCHAR(50) UNIQUE NOT NULL,
  password  VARCHAR(255) NOT NULL,
  role      ENUM('customer','admin') NOT NULL DEFAULT 'customer'
);

CREATE TABLE IF NOT EXISTS menu (
  item_id   INT AUTO_INCREMENT PRIMARY KEY,
  name      VARCHAR(100) NOT NULL,
  category  VARCHAR(50) NOT NULL,
  price     DECIMAL(8,2) NOT NULL CHECK (price > 0),
  is_veg    BOOLEAN NOT NULL DEFAULT TRUE,
  stock     INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
  available BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
  order_id   INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  total      DECIMAL(10,2) NOT NULL,
  status     ENUM('placed','preparing','served') NOT NULL DEFAULT 'placed',
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS order_items (
  order_id   INT NOT NULL,
  item_id    INT NOT NULL,
  quantity   INT NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (order_id, item_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (item_id)  REFERENCES menu(item_id)
);

CREATE TABLE IF NOT EXISTS feedback (
  feedback_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  order_id    INT,
  type        ENUM('feedback','complaint') NOT NULL DEFAULT 'feedback',
  rating      INT CHECK (rating BETWEEN 1 AND 5),
  comments    TEXT,
  resolved    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)  REFERENCES users(user_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO menu (name, category, price, is_veg, stock)
SELECT * FROM (
  SELECT 'Paneer Tikka' AS name, 'Starters' AS category, 180.00 AS price, TRUE AS is_veg, 30 AS stock
  UNION ALL SELECT 'Chicken 65', 'Starters', 200.00, FALSE, 25
  UNION ALL SELECT 'Veg Spring Rolls', 'Starters', 120.00, TRUE, 40
  UNION ALL SELECT 'Butter Chicken', 'Main Course', 280.00, FALSE, 20
  UNION ALL SELECT 'Dal Makhani', 'Main Course', 190.00, TRUE, 30
  UNION ALL SELECT 'Veg Biryani', 'Main Course', 170.00, TRUE, 35
  UNION ALL SELECT 'Chicken Biryani', 'Main Course', 240.00, FALSE, 30
  UNION ALL SELECT 'Butter Naan', 'Breads', 40.00, TRUE, 80
  UNION ALL SELECT 'Gulab Jamun', 'Desserts', 80.00, TRUE, 50
  UNION ALL SELECT 'Ice Cream Sundae', 'Desserts', 110.00, TRUE, 40
  UNION ALL SELECT 'Masala Chai', 'Beverages', 30.00, TRUE, 100
  UNION ALL SELECT 'Cold Coffee', 'Beverages', 90.00, TRUE, 60
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM menu);
