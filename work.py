import sqlite3


def first_select_user(chat_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE telegram_id = ?
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()
    return user


def register_user(chat_id, full_name, phone):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO users(telegram_id, full_name, phone)
    VALUES (?,?,?);
    ''', (chat_id, full_name, phone))
    database.commit()
    database.close()


def create_cart(chat_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO carts(user_id) VALUES (
        (
            SELECT user_id FROM users WHERE telegram_id = ?
        )
    )
    ''', (chat_id,))
    database.commit()
    database.close()


def get_categories():
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM categories;
    ''')
    categories = cursor.fetchall()  # [(1, Лаваши), (2, Бургеры)]
    database.close()
    return categories


def get_products_by_category(category_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_id, product_name
    FROM products WHERE category_id = ?
    ''', (category_id,))
    products = cursor.fetchall()
    database.close()
    return products


def get_product(product_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM products WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()  # (1, 1, 'Минилаваш', ....)
    database.close()
    return product


def get_user_cart_id(chat_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_id FROM carts WHERE user_id = (
        SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))
    cart_id = cursor.fetchone()[0]
    database.close()
    return cart_id


def insert_or_update_cart_product(cart_id, product_name, quantity, final_price):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
        INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
        VALUES (?,?,?,?)
        ''', (cart_id, product_name, quantity, final_price))
        database.commit()
        return True
    except Exception as e:
        print(e)
        cursor.execute('''
        UPDATE cart_products
        SET quantity = ?,
        final_price = ?
        WHERE product_name = ? AND cart_id = ?
        ''', (quantity, final_price, product_name, cart_id))
        database.commit()
        return False
    finally:
        database.close()


def update_total_product_total_price(cart_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    UPDATE carts
    SET total_products = (
        SELECT SUM(quantity) FROM cart_products
        WHERE cart_id = :cart_id
    ),
    total_price = (
        SELECT SUM(final_price) FROM cart_products
        WHERE cart_id = :cart_id
    )
    WHERE cart_id = :cart_id
    ''', {'cart_id': cart_id})
    database.commit()
    database.close()


def select_order(chat_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute(''' 
    SELECT * FROM orders WHERE telegram_id=?;

    ''', (chat_id,))
    select_history = cursor.fetchall()
    print(select_history)
    return select_history


def get_total_products_price(cart_id):
    # Функция вывода общей голичества товаров и общей цены
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT total_products, total_price FROM carts WHERE cart_id = ?;

    ''', (cart_id,))
    total_products, total_price = cursor.fetchone()
    database.close()
    return total_products, total_price


def get_cart_products(cart_id):
    """Получение информации о товарах в корзине"""
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_product_id, product_name, quantity, final_price
    FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products


def delete_cart_product(cart_product_id):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    cursor.execute('''
    DELETE FROM cart_products WHERE cart_product_id = ?
    ''', (cart_product_id,))
    database.commit()
    database.close()


def add_order(cart_id, telegram_id, text, price):
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    cursor.execute(''' 
        INSERT INTO orders(cart_id,telegram_id,text,price) VALUES(?,?,?,?) 
    ''', (cart_id, telegram_id, text, price,))
    database.commit()
    # database.close()

