
import pymysql

password = input("Enter MySQL root password:")

try:
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password=password,
        port=3306
    )

    print("MySQL connection successful!")
    connection.close()

except pymysql.MySQLError as e:
    print("MySQL connection failed:")
    print(e)
