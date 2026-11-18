
import pymysql

password = input("Enter MySQL root password: ")

try:
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password=password,
        port=3306
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS retail_sales_db
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """)

    print("Database created successfully!")

    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()

    print("\nAvailable databases:")
    for db in databases:
        print(db[0])

    cursor.close()
    connection.close()

except pymysql.MySQLError as e:
    print("Error:", e)
