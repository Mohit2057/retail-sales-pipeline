
import os
import re
from datetime import datetime

import pymysql
from fastapi import FastAPI, HTTPException, Query


app = FastAPI(
    title="Retail Sales Pipeline API",
    version="1.0.0"
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    password = os.getenv("MYSQL_PASSWORD")

    if not password:
        raise RuntimeError(
            "MYSQL_PASSWORD environment variable is not set."
        )

    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password=password,
        database="retail_sales_db",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )


# --------------------------------------------------
# HELPER FUNCTION: VALIDATE MONTH
# --------------------------------------------------

def get_month_date(month):

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise HTTPException(
            status_code=422,
            detail="Invalid month format. Use YYYY-MM."
        )

    return datetime.strptime(month, "%Y-%m").date().replace(day=1)


def next_month_date(month_date):

    if month_date.month == 12:
        return month_date.replace(
            year=month_date.year + 1,
            month=1
        )

    return month_date.replace(month=month_date.month + 1)


# --------------------------------------------------
# 1. HEALTH CHECK API
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "message": "Retail Sales API is running"
    }


# --------------------------------------------------
# 2. CUSTOMER SUMMARY API
# --------------------------------------------------

@app.get("/customers/{customer_id}/summary")
def customer_summary(customer_id: str):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            query = """
                SELECT
                    c.customer_id,

                    COUNT(DISTINCT f.invoice_no) AS total_orders,

                    COALESCE(SUM(f.quantity), 0) AS total_quantity,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN f.is_non_product = FALSE
                                 AND f.is_free_sample = FALSE
                                THEN f.gross_gbp
                                ELSE 0
                            END
                        ), 0
                    ) AS total_revenue_gbp,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN f.is_non_product = FALSE
                                 AND f.is_free_sample = FALSE
                                THEN f.gross_usd
                                ELSE 0
                            END
                        ), 0
                    ) AS total_revenue_usd

                FROM dim_customer c

                LEFT JOIN fact_invoice_lines f
                    ON c.customer_key = f.customer_key

                WHERE c.customer_id = %s
                  AND c.is_placeholder = FALSE

                GROUP BY c.customer_id
            """

            cursor.execute(query, (customer_id,))

            result = cursor.fetchone()

            if result is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )

            return result

    finally:
        connection.close()


# --------------------------------------------------
# 3. TOP PRODUCTS API
# --------------------------------------------------

@app.get("/products/top")
def top_products(
    month: str,
    limit: int = Query(default=10, ge=1, le=100)
):

    start_date = get_month_date(month)
    end_date = next_month_date(start_date)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            query = """
                SELECT
                    p.stock_code,
                    p.description,

                    SUM(f.quantity) AS total_quantity,

                    ROUND(SUM(f.gross_usd), 2)
                        AS total_revenue_usd

                FROM fact_invoice_lines f

                JOIN dim_product p
                    ON f.product_key = p.product_key

                WHERE f.invoice_date >= %s
                  AND f.invoice_date < %s

                  AND p.is_non_product = FALSE
                  AND f.is_non_product = FALSE
                  AND f.is_free_sample = FALSE

                GROUP BY
                    p.stock_code,
                    p.description

                ORDER BY total_revenue_usd DESC

                LIMIT %s
            """

            cursor.execute(
                query,
                (start_date, end_date, limit)
            )

            results = cursor.fetchall()

            return {
                "month": month,
                "limit": limit,
                "total_products": len(results),
                "top_products": results
            }

    finally:
        connection.close()


# --------------------------------------------------
# 4. MONTHLY KPI API
# --------------------------------------------------

@app.get("/kpis/monthly")
def monthly_kpis(
    start: str,
    end: str,
    region: str = None
):

    start_date = get_month_date(start)
    end_month_date = get_month_date(end)

    if start_date > end_month_date:
        raise HTTPException(
            status_code=422,
            detail="Start month cannot be after end month."
        )

    end_date = next_month_date(end_month_date)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            query = """
                SELECT

                    CONCAT(
                        YEAR(f.invoice_date),
                        '-',
                        LPAD(MONTH(f.invoice_date), 2, '0')
                    ) AS month,

                    COUNT(DISTINCT f.invoice_no) AS total_orders,

                    COUNT(*) AS total_invoice_lines,

                    SUM(f.quantity) AS total_quantity,

                    ROUND(
                        SUM(
                            CASE
                                WHEN f.is_non_product = FALSE
                                 AND f.is_free_sample = FALSE
                                THEN f.gross_gbp
                                ELSE 0
                            END
                        ), 2
                    ) AS revenue_gbp,

                    ROUND(
                        SUM(
                            CASE
                                WHEN f.is_non_product = FALSE
                                 AND f.is_free_sample = FALSE
                                THEN f.gross_usd
                                ELSE 0
                            END
                        ), 2
                    ) AS revenue_usd

                FROM fact_invoice_lines f

                JOIN dim_country c
                    ON f.country_key = c.country_key

                WHERE f.invoice_date >= %s
                  AND f.invoice_date < %s

                  AND (%s IS NULL OR c.region = %s)

                GROUP BY
                    CONCAT(
                        YEAR(f.invoice_date),
                        '-',
                        LPAD(MONTH(f.invoice_date), 2, '0')
                    )

                ORDER BY MIN(f.invoice_date)
            """

            cursor.execute(
                query,
                (start_date, end_date, region, region)
            )

            results = cursor.fetchall()

            return {
                "start_month": start,
                "end_month": end,
                "region": region,
                "monthly_kpis": results
            }

    finally:
        connection.close()


# --------------------------------------------------
# 5. DATA QUALITY SUMMARY API
# --------------------------------------------------

@app.get("/data-quality/summary")
def data_quality_summary():

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            query = """
                SELECT
                    rule_code,
                    COUNT(*) AS issue_count

                FROM data_quality_issue

                GROUP BY rule_code

                ORDER BY rule_code
            """

            cursor.execute(query)

            results = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) AS total_issues
                FROM data_quality_issue
            """)

            total = cursor.fetchone()["total_issues"]

            return {
                "total_issues": total,
                "issues_by_rule": results
            }

    finally:
        connection.close()
