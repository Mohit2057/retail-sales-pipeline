
import pandas as pd
import pymysql

INPUT_FILE = "data/processed/retail_after_r8.csv"
REJECTED_FILE = "data/processed/rejected_negative_prices.csv"
BATCH_SIZE = 10000

password = input("Enter MySQL root password: ")

connection = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password=password,
    database="retail_sales_db",
    port=3306
)

insert_query = """
INSERT INTO data_quality_issue
(rule_code, invoice_no, stock_code, issue_description)
VALUES (%s, %s, %s, %s)
"""

try:
    with connection.cursor() as cursor:

        # Make this script safe to rerun
        cursor.execute("""
            DELETE FROM data_quality_issue
            WHERE rule_code IN (
                'R2_CANCEL',
                'R2_NEG_QTY',
                'R4_NON_PRODUCT',
                'R5_FREE_SAMPLE',
                'R5_NEG_PRICE',
                'R8_UNKNOWN'
            )
        """)

        total_logged = 0

        # Process accepted transaction records in chunks
        for chunk in pd.read_csv(
            INPUT_FILE,
            encoding="latin1",
            chunksize=BATCH_SIZE
        ):

            chunk["Invoice"] = chunk["Invoice"].astype("string")
            chunk["Quantity"] = pd.to_numeric(
                chunk["Quantity"], errors="coerce"
            )

            invoice = chunk["Invoice"].str.strip()
            cancellation = invoice.str.upper().str.startswith(
                "C", na=False
            )

            negative_non_cancel = (
                (chunk["Quantity"] < 0) & (~cancellation)
            )

            issue_groups = [
                (
                    "R2_CANCEL",
                    cancellation,
                    "Cancellation invoice"
                ),
                (
                    "R2_NEG_QTY",
                    negative_non_cancel,
                    "Negative quantity on non-cancellation invoice"
                ),
                (
                    "R4_NON_PRODUCT",
                    chunk["is_non_product"].fillna(False).astype(bool),
                    "Non-product code excluded from product revenue"
                ),
                (
                    "R5_FREE_SAMPLE",
                    chunk["is_free_sample"].fillna(False).astype(bool),
                    "Zero-price free sample excluded from revenue"
                ),
                (
                    "R8_UNKNOWN",
                    chunk["region"].eq("Unknown"),
                    "Country mapped to Unknown region"
                )
            ]

            for rule, mask, description in issue_groups:

                selected = chunk.loc[mask]

                records = [
                    (
                        rule,
                        None if pd.isna(row["Invoice"])
                        else str(row["Invoice"]),
                        None if pd.isna(row["StockCode"])
                        else str(row["StockCode"]),
                        description
                    )
                    for _, row in selected.iterrows()
                ]

                if records:
                    cursor.executemany(insert_query, records)
                    total_logged += len(records)

        # Log rejected negative-price records
        rejected = pd.read_csv(
            REJECTED_FILE,
            encoding="latin1"
        )

        rejected_records = [
            (
                "R5_NEG_PRICE",
                None if pd.isna(row["Invoice"])
                else str(row["Invoice"]),
                None if pd.isna(row["StockCode"])
                else str(row["StockCode"]),
                "Negative price - rejected from accepted dataset"
            )
            for _, row in rejected.iterrows()
        ]

        if rejected_records:
            cursor.executemany(insert_query, rejected_records)
            total_logged += len(rejected_records)

    connection.commit()

    print("Data quality issues loaded successfully!")
    print("Total issue records:", total_logged)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rule_code, COUNT(*) AS issue_count
            FROM data_quality_issue
            GROUP BY rule_code
            ORDER BY rule_code
        """)

        print("\nIssues by rule:")
        for row in cursor.fetchall():
            print(row)

except Exception as e:
    connection.rollback()
    print("Loading failed:", e)

finally:
    connection.close()
