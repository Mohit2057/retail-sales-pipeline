
import pandas as pd
import pymysql

# Read cleaned data
df = pd.read_csv(
    "data/processed/retail_after_r8.csv",
    encoding="latin1"
)

# Select country information
countries = df[
    ["Country", "country_standardized", "region"]
].copy()

# Rename columns according to MySQL table
countries = countries.rename(columns={
    "Country": "country_raw",
    "country_standardized": "country_name"
})

# Handle missing values
countries["country_raw"] = countries["country_raw"].fillna("Unknown")
countries["country_name"] = countries["country_name"].fillna("Unknown")
countries["region"] = countries["region"].fillna("Unknown")

# Remove duplicate country records
countries = countries.drop_duplicates(
    subset=["country_raw"]
)

# Prepare records
records = [
    (
        str(row["country_raw"]).strip(),
        str(row["country_name"]).strip(),
        str(row["region"]).strip()
    )
    for _, row in countries.iterrows()
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
        INSERT IGNORE INTO dim_country
        (country_raw, country_name, region)
        VALUES (%s, %s, %s)
        """

        cursor.executemany(query, records)

    connection.commit()

    print("Country dimension loaded successfully!")
    print("Unique countries:", len(records))

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM dim_country")
        print("Total countries in MySQL:", cursor.fetchone()[0])

finally:
    connection.close()
