
import pandas as pd
import pymysql

# Read cleaned data
df = pd.read_csv(
    "data/processed/retail_after_r8.csv",
    encoding="latin1"
)

# Clean product codes
df["stock_code_clean"] = (
    df["StockCode"].astype("string").str.strip().str.upper()
)

# Remove empty stock codes
df = df.dropna(subset=["stock_code_clean"])
df = df[df["stock_code_clean"] != ""]

# Create one record per product code
products = (
    df.groupby("stock_code_clean")
    .agg(
        description=("Description", "first"),
        is_non_product=("is_non_product", "max")
    )
    .reset_index()
)

# Prepare records for MySQL
records = [
    (
        row["stock_code_clean"],
        None if pd.isna(row["description"]) else str(row["description"]),
        bool(row["is_non_product"])
    )
    for _, row in products.iterrows()
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
        INSERT IGNORE INTO dim_product
        (stock_code, description, is_non_product)
        VALUES (%s, %s, %s)
        """

        cursor.executemany(query, records)

    connection.commit()

    print("Product dimension loaded successfully!")
    print("Unique products:", len(records))

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM dim_product")
        print("Total products in MySQL:", cursor.fetchone()[0])

finally:
    connection.close()
