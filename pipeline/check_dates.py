
import pandas as pd

file_path = "data/raw/online_retail_II.csv"

# Read original CSV
df = pd.read_csv(file_path, encoding="latin1")

raw_dates = df["InvoiceDate"].astype("string").str.strip()

print("\n========== ORIGINAL DATE ANALYSIS ==========")

# 1. Actual missing values
print("Original NULL values:", raw_dates.isna().sum())

# 2. Empty strings
print(
    "Empty date strings:",
    raw_dates.eq("").sum()
)

# 3. Original date samples
print("\nRandom Original Date Values:")
print(
    raw_dates.dropna()
    .sample(20, random_state=42)
    .to_string(index=False)
)

# 4. Parse dates
parsed_dates = pd.to_datetime(
    raw_dates,
    format="mixed",
    errors="coerce"
)

# 5. Invalid date values
invalid_mask = raw_dates.notna() & parsed_dates.isna()

print("\nInvalid Date Count:", invalid_mask.sum())

print("\nInvalid Date Examples:")
print(raw_dates[invalid_mask].head(20).to_string(index=False))

# 6. Dates before December 2009
print("\nDates Before December 2009:")

early_mask = parsed_dates < "2009-12-01"

print("Count:", early_mask.sum())

print(raw_dates[early_mask].head(20).to_string(index=False))

print("\n========== FINAL DATE RANGE ==========")

print("Minimum Date:", parsed_dates.min())
print("Maximum Date:", parsed_dates.max())

print("Total Valid Dates:", parsed_dates.notna().sum())
print("Total Invalid Dates:", parsed_dates.isna().sum())