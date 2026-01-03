-- Active: 1764687319910@@127.0.0.1@5432@Pharmacy_DB
CREATE TABLE IF NOT EXISTS raw.pharmacy_sales (
    distributor          VARCHAR(255),
    customer_name        VARCHAR(255),
    city                 VARCHAR(100),
    country              VARCHAR(100),
    latitude             DOUBLE PRECISION,
    longitude            DOUBLE PRECISION,
    channel              VARCHAR(100),
    sub_channel          VARCHAR(100),
    product_name         VARCHAR(255),
    product_class        VARCHAR(150),
    quantity             DOUBLE PRECISION,
    price                DOUBLE PRECISION,
    sales                DOUBLE PRECISION,
    month                VARCHAR(20),
    year                 INT,
    sales_rep_name       VARCHAR(255),
    manager              VARCHAR(255),
    sales_team           VARCHAR(100)
);

CREATE OR REPLACE VIEW features.sales_llm_context AS
SELECT
    distributor,
    customer_name,
    city,
    country,
    latitude,
    longitude,
    channel,
    sub_channel,
    product_name,
    product_class,
    sales_team,
    sales_rep_name,
    manager,
    month,
    year,

    -- aggregated metrics
    SUM(quantity) AS total_quantity,
    AVG(price)    AS avg_price,
    SUM(sales)    AS total_sales,

    CASE
        WHEN SUM(quantity) > 0
        THEN SUM(sales) / SUM(quantity)
        ELSE 0
    END AS avg_revenue_per_unit

FROM raw.pharmacy_sales
GROUP BY
    distributor,
    customer_name,
    city,
    country,
    latitude,
    longitude,
    channel,
    sub_channel,
    product_name,
    product_class,
    sales_team,
    sales_rep_name,
    manager,
    month,
    year;

-- airflow sql file was created to create sales features table before airflow ingestion training process
CREATE TABLE IF NOT EXISTS features.sales_feature AS
SELECT
    distributor,
    channel,
    sub_channel,
    city,
    product_name,
    product_class,
    sales_team,
    year,
    month,
    SUM(quantity) AS total_quantity,
    AVG(Price) AS avg_price,
    SUM(Sales) AS total_sales
FROM raw.pharmacy_sales
GROUP BY
    distributor,
    channel,
    sub_channel,
    city,
    product_name,
    product_class,
    sales_team,
    year,
    month;

SELECT * FROM raw.pharmacy_sales;
SELECT * FROM features.sales_llm_context;
SELECT * FROM features.sales_feature;
SELECT * FROM features.pharmacy_sales_enhanced;