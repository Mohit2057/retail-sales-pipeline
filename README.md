# Retail Sales Pipeline

A data engineering project that processes retail transaction data, applies data quality rules, performs currency conversion and country-region mapping, and loads the transformed data into a MySQL star schema. A FastAPI layer is included to expose selected data through API endpoints.

## Tech Stack

- Python
- Pandas
- MySQL
- FastAPI
- SQL

## Project Workflow

1. Extract retail transaction data.
2. Remove exact duplicate records.
3. Identify cancellations and negative quantities.
4. Handle missing Customer IDs.
5. Identify non-product transaction codes.
6. Validate prices and calculate gross revenue in GBP.
7. Convert GBP revenue into USD using historical FX rates.
8. Map countries to regions.
9. Load dimensions and fact records into MySQL.
10. Expose selected data through FastAPI endpoints.

## Database Design

The MySQL database is named `retail_sales_db`.

Tables include:

- `dim_customer`
- `dim_product`
- `dim_country`
- `dim_date`
- `fact_invoice_lines`
- `data_quality_issue`

## Current Implementation Status

### Working

- Python ETL scripts for data extraction and transformation.
- Duplicate removal and data quality checks.
- Cancellation, customer, non-product and price handling.
- GBP revenue calculation and FX conversion.
- Country-to-region mapping.
- MySQL database and star schema creation.
- Loading of dimension, fact and data quality records.
- FastAPI health endpoint (`/health`) returns HTTP 200.

### Incomplete / Known Issues

The FastAPI application is included, but the customer summary endpoint is currently returning HTTP 500.

The application reads the MySQL password from the `MYSQL_PASSWORD` environment variable. Environment-variable configuration and application logs were checked during troubleshooting, but the customer endpoint issue remains unresolved.

The following endpoints are implemented but have not all been fully verified:

- `/customers/{customer_id}/summary`
- `/products/top`
- `/kpis/monthly`
- `/data-quality/summary`

The API implementation is therefore included as work in progress.

## Dataset Note

The project was implemented using the CSV source file `online_retail_II.csv`. The original assignment specified an Excel workbook with two sheets. The CSV source was used instead, so this is a deviation from the specified input format.

Supporting reference files used:

- `fx_rates_gbp_usd.csv`
- `country_region.csv`
- `non_product_codes.csv`

The large source dataset is excluded from this Git repository.

## Important Results

- Rows after duplicate removal: 1,033,034
- Accepted rows after price validation: 1,033,031
- Fact records loaded into MySQL: 1,033,031
- Gross revenue in GBP: 19,014,209.838
- Converted revenue in USD: 30,014,787.73465
- Missing FX rates: 0
- Future FX rates used: 0

## Security

The MySQL password is read through the `MYSQL_PASSWORD` environment variable. Do not commit database passwords or `.env` files to GitHub.

## Repository Structure

```text
retail-sales-pipeline/
├── data/
│   ├── raw/
│   └── reference/
├── pipeline/
├── sql/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Future Improvements

- Resolve and verify FastAPI database connectivity.
- Test all API endpoints.
- Add automated ETL validation tests.
- Improve project setup and execution documentation.

