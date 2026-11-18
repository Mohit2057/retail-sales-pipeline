
import pandas as pd
import pymysql
from decimal import Decimal

INPUT_FILE = "data/processed/retail_after_r8.csv"
BATCH_SIZE = 10000

password = input("Enter MySQL root password: ")

connection = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password=password,
    database="retail_sales_db",
    port=3306
)

def clean_text(value):
    if pd.isna(value):
        return None
    return str(value).strip()

def to_decimal(value):
    if pd.isna(value):
        return None
    return Decimal(str(value))

try:
    with connection.cursor() as cursor:

        # Fetch dimension key mappings
        cursor.execute(
            "SELECT customer_key, customer_id FROM dim_customer"
        )
        customer_map = {
            str(customer_id): key
            for key, customer_id in cursor.fetchall()
        }

        cursor.execute(
            "SELECT product_key, stock_code FROM dim_product"
        )
        product_map = {
            str(code).strip().upper(): key
            for key, code in cursor.fetchall()
        }

        cursor.execute(
            "SELECT country_key, country_raw FROM dim_country"
        )
        country_map = {
            str(country).strip().casefold(): key
            for key, country in cursor.fetchall()
        }

        cursor.execute(
            "SELECT date_key, full_date FROM dim_date"
        )
        date_map = {
            str(full_date): key
            for key, full_date in cursor.fetchall()
        }

        insert_query = """
        INSERT INTO fact_invoice_lines (
            invoice_no,
            invoice_date,
            customer_key,
            product_key,
            country_key,
            date_key,
            quantity,
            unit_price_gbp,
            gross_gbp,
            fx_rate_used,
            fx_rate_date,
            gross_usd,
            is_cancellation,
            is_negative_quantity,
            is_non_product,
            is_free_sample
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """

        total_inserted = 0

        # Read data in batches
        for chunk in pd.read_csv(
            INPUT_FILE,
            encoding="latin1",
            dtype={
                "Invoice": "string",
                "StockCode": "string",
                "Customer ID": "string",
                "customer_id_clean": "string",
                "Country": "string",
                "gross_gbp": "string",
                "gross_usd": "string",
                "fx_rate_used": "string",
                "Price": "string"
            },
            chunksize=BATCH_SIZE
        ):

            chunk["InvoiceDate"] = pd.to_datetime(
                chunk["InvoiceDate"],
                format="mixed",
                errors="coerce"
            )

            if chunk["InvoiceDate"].isna().any():
                raise ValueError("Invalid invoice date found.")

            chunk["country_lookup"] = (
                chunk["Country"]
                .fillna("Unknown")
                .str.strip()
                .str.casefold()
            )

            chunk["product_lookup"] = (
                chunk["StockCode"]
                .str.strip()
                .str.upper()
            )

            chunk["date_lookup"] = (
                chunk["InvoiceDate"].dt.strftime("%Y-%m-%d")
            )

            chunk["customer_id_clean"] = (
                chunk["customer_id_clean"].fillna("UNKNOWN")
            )

            chunk["customer_key"] = (
                chunk["customer_id_clean"].map(customer_map)
            )

            chunk["product_key"] = (
                chunk["product_lookup"].map(product_map)
            )

            chunk["country_key"] = (
                chunk["country_lookup"].map(country_map)
            )

            chunk["date_key"] = (
                chunk["date_lookup"].map(date_map)
            )

            # Validate foreign key mappings before inserting
            key_columns = [
                "customer_key",
                "product_key",
                "country_key",
                "date_key"
            ]

            if chunk[key_columns].isna().any().any():
                raise ValueError(
                    "Missing dimension key found. "
                    "Check customer, product, country and date mappings."
                )

            records = []

            for row in chunk.itertuples(index=False):

                invoice_date = row.InvoiceDate.to_pydatetime()
                quantity = int(row.Quantity)

                records.append((
                    clean_text(row.Invoice),
                    invoice_date,
                    int(row.customer_key),
                    int(row.product_key),
                    int(row.country_key),
                    int(row.date_key),
                    quantity,
                    to_decimal(row.Price),
                    to_decimal(row.gross_gbp),
                    to_decimal(row.fx_rate_used),
                    pd.to_datetime(row.fx_rate_date).date(),
                    to_decimal(row.gross_usd),
                    str(row.Invoice).strip().upper().startswith("C"),
                    quantity < 0,
                    bool(row.is_non_product),
                    bool(row.is_free_sample)
                ))

            cursor.executemany(insert_query, records)

            total_inserted += len(records)

            print("Rows inserted:", total_inserted)

    connection.commit()

    print("--------------------------------")
    print("Fact table loaded successfully!")
    print("Total inserted rows:", total_inserted)

except Exception as e:
    connection.rollback()
    print("Fact loading failed:", e)

finally:
    connection.close()
