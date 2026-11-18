
import pandas as pd

# Read data after R2
input_file = "data/processed/retail_after_r2.csv"
df = pd.read_csv(input_file, encoding="latin1")

# Count missing Customer IDs
missing_before = df["Customer ID"].isna().sum()

# Create a cleaned customer ID column
df["customer_id_clean"] = (
    df["Customer ID"]
    .astype("string")
    .str.strip()
)

# Replace missing or blank IDs with one placeholder
df["customer_id_clean"] = df["customer_id_clean"].replace(
    "", pd.NA
)

df["is_placeholder_customer"] = (
    df["customer_id_clean"].isna()
)

df["customer_id_clean"] = df["customer_id_clean"].fillna(
    "UNKNOWN"
)

# Count actual customers, excluding placeholder
actual_customers = df.loc[
    ~df["is_placeholder_customer"],
    "customer_id_clean"
].nunique()

placeholder_rows = df["is_placeholder_customer"].sum()

# Save processed data
output_file = "data/processed/retail_after_r3.csv"
df.to_csv(output_file, index=False)

print("R3 - Missing Customer ID Handling")
print("----------------------------------")
print("Missing Customer IDs before:", missing_before)
print("Rows assigned to placeholder:", placeholder_rows)
print("Distinct actual customers:", actual_customers)
print("Total rows after R3:", len(df))
print("Saved file:", output_file)
