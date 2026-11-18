
import pandas as pd
from pathlib import Path

print("\n========== R2: CANCELLATION ANALYSIS ==========")

# 1. Read R1 cleaned dataset
input_file = Path("data/processed/retail_after_r1.csv")

df = pd.read_csv(input_file, encoding="latin1")

print("Input Rows:", len(df))

# 2. Identify cancelled invoices
df["Invoice"] = df["Invoice"].astype("string").str.strip()

df["is_cancellation"] = (
    df["Invoice"].str.upper().str.startswith("C", na=False)
)

# 3. Identify negative quantities
df["is_negative_quantity"] = df["Quantity"] < 0

# 4. Identify negative quantities that are NOT cancellations
df["is_stock_writeoff"] = (
    df["is_negative_quantity"] &
    (~df["is_cancellation"])
)

# 5. Count each category separately
cancellation_count = df["is_cancellation"].sum()

negative_quantity_count = df["is_negative_quantity"].sum()

stock_writeoff_count = df["is_stock_writeoff"].sum()

print("\n========== R2 RESULTS ==========")

print("Cancellation Rows:", cancellation_count)

print("All Negative Quantity Rows:", negative_quantity_count)

print("Negative Quantity Non-Cancellations:", stock_writeoff_count)

print(
    "Negative Quantity on Cancellation Invoices:",
    (df["is_negative_quantity"] & df["is_cancellation"]).sum()
)

# 6. Save results
output_file = Path("data/processed/retail_after_r2.csv")

df.to_csv(output_file, index=False)

print("\nRemaining Rows:", len(df))
print("Output Saved:", output_file)

print("\n========== R2 COMPLETED ==========")
