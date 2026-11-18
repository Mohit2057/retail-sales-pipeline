
USE retail_sales_db;

-- 1. Customer dimension
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    is_placeholder BOOLEAN DEFAULT FALSE
);

-- 2. Product dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_non_product BOOLEAN DEFAULT FALSE
);

-- 3. Country dimension
CREATE TABLE IF NOT EXISTS dim_country (
    country_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    country_raw VARCHAR(100) NOT NULL UNIQUE,
    country_name VARCHAR(100),
    region VARCHAR(100)
);

-- 4. Date dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year SMALLINT,
    quarter TINYINT,
    month TINYINT,
    month_name VARCHAR(20),
    day TINYINT,
    weekday_name VARCHAR(20)
);

-- 5. Invoice fact table
CREATE TABLE IF NOT EXISTS fact_invoice_lines (
    line_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(30) NOT NULL,
    invoice_date DATETIME NOT NULL,

    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    country_key BIGINT NOT NULL,
    date_key INT NOT NULL,

    quantity INT,
    unit_price_gbp DECIMAL(18,6),
    gross_gbp DECIMAL(18,6),
    fx_rate_used DECIMAL(18,8),
    fx_rate_date DATE,
    gross_usd DECIMAL(18,6),

    is_cancellation BOOLEAN DEFAULT FALSE,
    is_negative_quantity BOOLEAN DEFAULT FALSE,
    is_non_product BOOLEAN DEFAULT FALSE,
    is_free_sample BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (country_key)
        REFERENCES dim_country(country_key),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    INDEX idx_invoice_no (invoice_no),
    INDEX idx_invoice_date (invoice_date),
    INDEX idx_customer_key (customer_key),
    INDEX idx_product_key (product_key),
    INDEX idx_country_key (country_key)
);

-- 6. Data quality issue log
CREATE TABLE IF NOT EXISTS data_quality_issue (
    issue_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rule_code VARCHAR(20) NOT NULL,
    invoice_no VARCHAR(30),
    stock_code VARCHAR(50),
    issue_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_rule_code (rule_code)
);
