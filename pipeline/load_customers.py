
import pandas as pd
import pymysql

# Read cleaned data
df = pd.read_csv(
    "data/processed/retail_after_r8.csv",
    encoding="latin1",
    dtype={"customer_id_clean": "string"}
)

# Select unique customers
customers = df[
    ["customer_id_clean", "is_placeholder_customer"]
].drop_duplicates()

# Remove missing customer IDs, if any
customers = customers.dropna(
    subset=["customer_id_clean"]
)

# Convert records into tuples
records = [
    (
        str(row["customer_id_clean"]),
        bool(row["is_placeholder_customer"])
    )
    for _, row in customers.iterrows()
]

# Connect to MySQL
password = input("Enter MySQL root password: ")

connection = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password=password,
    database="retail_sales_db",
    port=3306
)

try:
    with connection.cursor() as cursor:

        query = """
        INSERT IGNORE INTO dim_customer
        (customer_id, is_placeholder)
        VALUES (%s, %s)
        """

        cursor.executemany(query, records)

    connection.commit()

    print("Customer dimension loaded successfully!")
    print("Unique customer records:", len(records))

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM dim_customer")
        print("Total customers in MySQL:", cursor.fetchone()[0])

finally:
    connection.close()
