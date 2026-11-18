
import pandas as pd
from pathlib import Path

raw_folder = Path("data/raw")
reference_folder = Path("data/reference")

# Find the source file
csv_files = list(raw_folder.glob("*.csv"))
excel_files = list(raw_folder.glob("*.xlsx"))

print("\n========== SOURCE DATA ==========")

if csv_files:
    source_file = csv_files[0]

    print("Source:", source_file.name)
    print("Format: CSV")

    df = pd.read_csv(source_file, encoding="latin1")

    print("\nTotal Rows:", len(df))
    print("Total Columns:", len(df.columns))
    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nMissing Values:")
    print(df.isnull().sum())

elif excel_files:
    source_file = excel_files[0]

    excel = pd.ExcelFile(source_file, engine="openpyxl")

    print("Source:", source_file.name)
    print("Sheets:", excel.sheet_names)

    all_data = []

    for sheet in excel.sheet_names:
        df = pd.read_excel(source_file, sheet_name=sheet)

        all_data.append(df)

        print(f"\nSheet: {sheet}")
        print("Rows:", len(df))
        print("Columns:", len(df.columns))
        print(df.head())

    combined_df = pd.concat(all_data, ignore_index=True)

    print("\nCombined Rows:", len(combined_df))

else:
    raise FileNotFoundError("No CSV or Excel file found!")

# Inspect reference files
print("\n========== REFERENCE FILES ==========")

for file in reference_folder.glob("*.csv"):

    ref_df = pd.read_csv(file)

    print(f"\nFile: {file.name}")
    print("Rows:", len(ref_df))
    print("Columns:", ref_df.columns.tolist())
    print(ref_df.head())



# Additional Data Profiling

print("\n========== DATA PROFILING ==========")

# 1. Convert InvoiceDate into datetime
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce",
    dayfirst=True
)

# 2. Check date range
print("\nDate Range:")
print("Minimum Date:", df["InvoiceDate"].min())
print("Maximum Date:", df["InvoiceDate"].max())

# 3. Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# 4. Check duplicate records
print("\nExact Duplicate Rows:", df.duplicated().sum())

# 5. Check negative quantities
print("\nNegative Quantity Rows:",
      (df["Quantity"] < 0).sum())

# 6. Check cancelled invoices
print("\nCancelled Invoice Rows:",
      df["Invoice"].astype(str).str.startswith("C").sum())

# 7. Check negative prices
print("\nNegative Price Rows:",
      (df["Price"] < 0).sum())

# 8. Check zero prices
print("\nZero Price Rows:",
      (df["Price"] == 0).sum())



# Correct Date Conversion

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    format="mixed",
    errors="coerce"
)

print("\n========== DATE VALIDATION ==========")

print("Minimum Date:", df["InvoiceDate"].min())
print("Maximum Date:", df["InvoiceDate"].max())

print("Missing Dates:", df["InvoiceDate"].isna().sum())

print("\nInvalid Date Examples:")

invalid_dates = df.loc[
    df["InvoiceDate"].isna()
]

print(invalid_dates.head(10))
