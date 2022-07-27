import sqlite3

database = sqlite3.connect('fastfood.db')
cursor = database.cursor()


def create_users_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone TEXT
    )
    ''')
    # INT - INTEGER -2147483648 до 2147483647
    # BIGINT -9223372036854775808 до 9223372036854775808
    # TINYINT -128 до 127


def create_cart_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carts(
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(user_id) UNIQUE,
        total_products INTEGER DEFAULT 0,
        total_price DECIMAL(12, 2) DEFAULT 0
    )
    ''')


def create_cart_products_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
        cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER REFERENCES carts(cart_id),
        product_name TEXT,
        quantity INTEGER NOT NULL,
        final_price DECIMAL(12, 2) NOT NULL,

        UNIQUE(cart_id, product_name)
    )
    ''')


def create_categories_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(30) NOT NULL UNIQUE
    )
    ''')


def insert_categories():
    cursor.execute('''
    INSERT OR IGNORE INTO categories(category_name) VALUES
    ('Футболки'),
    ('Шорты'),
    ('Джинсы'),
    ('Кофты'),
    ('Красовки'),
    ('Брюки'),
    ('Юбки'),
    ('Толстовки')
    ''')


def create_products_table():
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            product_name VARCHAR(30) NOT NULL UNIQUE,
            price DECIMAL(12, 2) NOT NULL,
            description VARCHAR(150),
            image TEXT,

            FOREIGN KEY(category_id) REFERENCES categories(category_id)
        );
        '''
    )


def insert_products():
    cursor.execute('''
    INSERT INTO products(category_id, product_name, price, description, image)
    VALUES
    (1, 'Черно-красный', 45000, 'Новый вид одежды', 'media/futbolka.jpg'),
    (2, 'Желто-оранжевый', 40000, 'Удобно для лето)', 'media/shorti.jpg'),
    (3, 'Женские', 50000, 'Модно и круто!', 'media/jinsi.jpg'),
    (4, 'Корчнево-красный', 41000, 'Отличный вариант для осеньего месяца', 'media/kofta.jpg'),
    (5, 'Jordan', 100000, 'Идиальный вид что-бы показать другим)', 'media/krosovka.jpg'),
    (6, 'Classik', 50000, 'Купите по выгодной цене', 'media/bruki.jpg'),
    (7, 'Синие', 30000, 'Модно и точка', 'media/ubki.jpg'),
    (8, 'Зеленые', 81000, 'Круто и точка', 'media/tolstovka.jpg')
    ''')


def create_orders_table():
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS orders( 
            order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            telegram_id TEXT, 
            cart_id INTEGER REFERENCES carts(cart_id), 
            text TEXT, 
            price TEXT, 
            status TEXT NOT NULL DEFAULT 'nready' 
        ) 
    ''')


create_users_table()
create_cart_table()
create_cart_products_table()
create_categories_table()
insert_categories()
create_products_table()
insert_products()
create_orders_table()

database.commit()
database.close()
