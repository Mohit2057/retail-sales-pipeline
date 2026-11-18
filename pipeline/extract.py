
import pandas as pd
import hashlib
from pathlib import Path
from datetime import datetime

# 1. Source file location
SOURCE_FILE = Path("data/raw/online_retail_II.csv")

# 2. Check source file
if not SOURCE_FILE.exists():
    raise FileNotFoundError("Raw dataset not found!")

print("\n========== RAW DATA EXTRACTION ==========")

# 3. Calculate file hash
sha256 = hashlib.sha256()

with open(SOURCE_FILE, "rb") as file:
    for chunk in iter(lambda: file.read(1024 * 1024), b""):
        sha256.update(chunk)

file_hash = sha256.hexdigest()

# 4. Read raw data in chunks
total_rows = 0
columns = None

for chunk in pd.read_csv(
    SOURCE_FILE,
    encoding="latin1",
    chunksize=100000
):
    total_rows += len(chunk)

    if columns is None:
        columns = chunk.columns.tolist()

# 5. Validate expected columns
expected_columns = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country"
]

if columns != expected_columns:
    raise ValueError("Unexpected dataset columns!")

# 6. Generate extraction report
manifest = f"""
RAW DATA EXTRACTION REPORT

Source File: {SOURCE_FILE.name}
Extraction Time: {datetime.now().isoformat()}
Total Rows: {total_rows}
Total Columns: {len(columns)}

Columns:
{columns}

File Size: {SOURCE_FILE.stat().st_size} bytes

SHA256:
{file_hash}

Status: SUCCESS
Original source file preserved without modification.
"""

# 7. Save audit manifest
report_path = Path("data/raw/extraction_manifest.txt")
report_path.write_text(manifest, encoding="utf-8")

print(manifest)

print("Audit manifest saved successfully!")
