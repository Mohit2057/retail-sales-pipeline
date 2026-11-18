
import pandas as pd

# Read transaction data
df = pd.read_csv(
    "data/processed/retail_after_r6.csv",
    encoding="latin1"
)

# Read FX reference data
fx = pd.read_csv(
    "data/reference/fx_rates_gbp_usd.csv"
)

# Convert dates
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    format="mixed",
    errors="coerce"
)

fx["rate_date"] = pd.to_datetime(
    fx["rate_date"],
    errors="coerce"
)

# Keep only GBP to USD rates
fx = fx[
    (fx["from_currency"] == "GBP") &
    (fx["to_currency"] == "USD")
].copy()

# Clean and sort FX data
fx["rate"] = pd.to_numeric(fx["rate"], errors="coerce")
fx = fx.dropna(subset=["rate_date", "rate"])
fx = fx.sort_values("rate_date")

# Keep only required columns
fx = fx[["rate_date", "rate"]].rename(
    columns={
        "rate_date": "fx_rate_date",
        "rate": "fx_rate_used"
    }
)

# Sort transactions by date
df = df.dropna(subset=["InvoiceDate"])
df = df.sort_values("InvoiceDate")

# Match same-date or previous available exchange rate
df = pd.merge_asof(
    df,
    fx,
    left_on="InvoiceDate",
    right_on="fx_rate_date",
    direction="backward"
)

# Calculate USD revenue
df["gross_usd"] = (
    pd.to_numeric(df["gross_gbp"]) *
    df["fx_rate_used"]
)

# Check missing exchange rates
missing_rates = df["fx_rate_used"].isna().sum()

# Check that no future rate was used
future_rates = (
    df["fx_rate_date"] > df["InvoiceDate"]
).sum()

# Save final data
output_file = "data/processed/retail_after_r7.csv"
df.to_csv(output_file, index=False)

print("R7 - GBP to USD Conversion")
print("--------------------------------")
print("Total transaction rows:", len(df))
print("Missing FX rates:", missing_rates)
print("Future rates used:", future_rates)
print("Total GBP Revenue:", df["gross_gbp"].sum())
print("Total USD Revenue:", df["gross_usd"].sum())
print("Saved file:", output_file)
