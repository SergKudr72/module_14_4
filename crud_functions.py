import sqlite3
connection = sqlite3.connect("products.db")
cursor = connection.cursor()


def initiate_db():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INT NOT NULL
    ); 
    ''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON Products (title)")
    connection.commit()
    connection.close()


def insert_products():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Products')  # Очистка таблицы перед её заполнением

    for i in range(1, 5):
        cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)",
                   (f"Продукт {i}", f"Описание {i}", f"{i*100}"))

    connection.commit()
    connection.close()


def get_all_products():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return products



if __name__ == '__main__':
  initiate_db()
  insert_products()
  connection.close()
