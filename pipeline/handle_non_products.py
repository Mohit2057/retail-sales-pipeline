
import pandas as pd

# Read data after R3
input_file = "data/processed/retail_after_r3.csv"
df = pd.read_csv(input_file, encoding="latin1")

# Read non-product reference codes
reference_file = "data/reference/non_product_codes.csv"
non_products = pd.read_csv(reference_file)

# Normalize codes for case-insensitive matching
df["stock_code_clean"] = (
    df["StockCode"].astype("string").str.strip().str.upper()
)

non_products["stock_code_clean"] = (
    non_products["stock_code"].astype("string").str.strip().str.upper()
)

# Identify non-product rows
non_product_codes = set(non_products["stock_code_clean"])

df["is_non_product"] = df["stock_code_clean"].isin(
    non_product_codes
)

# Count rows excluded from product revenue
excluded_rows = df["is_non_product"].sum()

# Save processed data
output_file = "data/processed/retail_after_r4.csv"
df.to_csv(output_file, index=False)

print("R4 - Non-Product Code Handling")
print("--------------------------------")
print("Reference non-product codes:", len(non_product_codes))
print("Rows flagged as non-product:", excluded_rows)
print("Total rows:", len(df))
print("Rows retained:", len(df))
print("Saved file:", output_file)
