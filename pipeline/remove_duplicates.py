
import pandas as pd
from pathlib import Path

print("\n========== R1: REMOVE DUPLICATES ==========")

# 1. Define paths
source_file = Path("data/raw/online_retail_II.csv")
output_folder = Path("data/processed")

# 2. Create processed folder
output_folder.mkdir(parents=True, exist_ok=True)

# 3. Read original raw data
df = pd.read_csv(source_file, encoding="latin1")

print("Original Rows:", len(df))

# 4. Count exact duplicates
duplicate_count = df.duplicated().sum()

print("Duplicate Rows Found:", duplicate_count)

# 5. Remove exact duplicates
df_clean = df.drop_duplicates(keep="first")

# 6. Verify results
print("Rows After Cleaning:", len(df_clean))
print("Remaining Duplicates:", df_clean.duplicated().sum())

# 7. Save cleaned dataset separately
output_file = output_folder / "retail_after_r1.csv"

df_clean.to_csv(output_file, index=False)

print("\nCleaned file saved:", output_file)

print("\n========== R1 COMPLETED ==========")
