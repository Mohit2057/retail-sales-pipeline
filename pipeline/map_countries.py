
import pandas as pd

# Read transaction data after R7
df = pd.read_csv(
    "data/processed/retail_after_r7.csv",
    encoding="latin1"
)

# Read country reference file
country_ref = pd.read_csv(
    "data/reference/country_region.csv"
)

# Normalize country names for case-insensitive matching
df["country_clean"] = (
    df["Country"]
    .astype("string")
    .str.strip()
    .str.casefold()
)

country_ref["country_clean"] = (
    country_ref["country_raw"]
    .astype("string")
    .str.strip()
    .str.casefold()
)

# Create mapping dictionaries
country_mapping = country_ref.set_index(
    "country_clean"
)["country_name"].to_dict()

region_mapping = country_ref.set_index(
    "country_clean"
)["region"].to_dict()

# Map standardized country and region
df["country_standardized"] = (
    df["country_clean"].map(country_mapping).fillna("Unknown")
)

df["region"] = (
    df["country_clean"].map(region_mapping).fillna("Unknown")
)

# Count unknown rows
unknown_rows = (df["region"] == "Unknown").sum()

# Save processed data
output_file = "data/processed/retail_after_r8.csv"
df.to_csv(output_file, index=False)

print("R8 - Country Region Mapping")
print("--------------------------------")
print("Total transaction rows:", len(df))
print("Unknown country rows:", unknown_rows)
print("Distinct original countries:", df["Country"].nunique())
print("Distinct regions:", df["region"].nunique())
print("Saved file:", output_file)
