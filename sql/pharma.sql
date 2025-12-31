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

SELECT * FROM raw.pharmacy_sales;
