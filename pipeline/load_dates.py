
import pandas as pd
import pymysql

# Read cleaned transaction data
df = pd.read_csv(
    "data/processed/retail_after_r8.csv",
    encoding="latin1"
)

# Convert InvoiceDate into datetime
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    format="mixed",
    errors="coerce"
)

# Check invalid dates
invalid_dates = df["InvoiceDate"].isna().sum()

if invalid_dates > 0:
    raise ValueError(
        f"Found {invalid_dates} invalid transaction dates."
    )

# Extract unique calendar dates
dates = pd.DataFrame({
    "full_date": df["InvoiceDate"].dt.normalize().drop_duplicates()
})

# Generate date attributes
dates["date_key"] = (
    dates["full_date"].dt.strftime("%Y%m%d").astype(int)
)

dates["year"] = dates["full_date"].dt.year
dates["quarter"] = dates["full_date"].dt.quarter
dates["month"] = dates["full_date"].dt.month
dates["month_name"] = dates["full_date"].dt.month_name()
dates["day"] = dates["full_date"].dt.day
dates["weekday_name"] = dates["full_date"].dt.day_name()

# Prepare records
records = [
    (
        int(row.date_key),
        row.full_date.date(),
        int(row.year),
        int(row.quarter),
        int(row.month),
        row.month_name,
        int(row.day),
        row.weekday_name
    )
    for row in dates.itertuples(index=False)
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
        INSERT IGNORE INTO dim_date
        (
            date_key,
            full_date,
            year,
            quarter,
            month,
            month_name,
            day,
            weekday_name
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.executemany(query, records)

    connection.commit()

    print("Date dimension loaded successfully!")
    print("Unique dates:", len(records))

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM dim_date")
        print("Total dates in MySQL:", cursor.fetchone()[0])

finally:
    connection.close()
