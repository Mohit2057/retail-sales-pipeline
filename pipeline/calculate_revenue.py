
import pandas as pd
from decimal import Decimal, InvalidOperation

# Read data after R5
input_file = "data/processed/retail_after_r5.csv"
df = pd.read_csv(input_file, encoding="latin1")

# Calculate exact GBP amount using Decimal
def calculate_gross_gbp(row):
    try:
        quantity = Decimal(str(row["Quantity"]))
        price = Decimal(str(row["Price"]))
        return quantity * price
    except (InvalidOperation, ValueError):
        return Decimal("0")

df["gross_gbp"] = df.apply(calculate_gross_gbp, axis=1)

# Calculate total gross revenue without early rounding
total_gbp = sum(df["gross_gbp"], Decimal("0"))

# Save processed data
output_file = "data/processed/retail_after_r6.csv"
df.to_csv(output_file, index=False)

print("R6 - Gross Revenue Calculation")
print("--------------------------------")
print("Total transaction rows:", len(df))
print("Total Gross Revenue GBP:", total_gbp)
print("Free sample rows:", int(df["is_free_sample"].sum()))
print("Saved file:", output_file)
