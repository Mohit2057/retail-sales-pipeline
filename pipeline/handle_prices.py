
import pandas as pd

# Read data after R4
input_file = "data/processed/retail_after_r4.csv"
df = pd.read_csv(input_file, encoding="latin1")

# Convert Price into numeric values
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

# Identify negative prices
negative_price = df["Price"] < 0

# Identify zero-price free samples
free_sample = df["Price"] == 0

# Separate rejected rows for audit
rejected_df = df[negative_price].copy()
rejected_df["quality_rule"] = "R5_NEGATIVE_PRICE"
rejected_df["issue_description"] = "Negative price - rejected"

# Keep rows with zero or positive prices
accepted_df = df[~negative_price].copy()

# Add free sample flag
accepted_df["is_free_sample"] = (
    accepted_df["Price"] == 0
)

# Save rejected records
rejected_file = "data/processed/rejected_negative_prices.csv"
rejected_df.to_csv(rejected_file, index=False)

# Save accepted records
output_file = "data/processed/retail_after_r5.csv"
accepted_df.to_csv(output_file, index=False)

print("R5 - Price Handling")
print("--------------------")
print("Negative price rows rejected:", len(rejected_df))
print("Zero price free samples:", int(free_sample.sum()))
print("Accepted rows:", len(accepted_df))
print("Total original rows:", len(df))
print("Rejected file:", rejected_file)
print("Processed file:", output_file)
