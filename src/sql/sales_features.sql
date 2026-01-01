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

SELECT * FROM features.sales_feature;

SELECT * FROM features.sales_llm_context;