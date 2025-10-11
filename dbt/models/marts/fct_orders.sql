SELECT
    order_id,
    customer_id,
    order_month,
    SUM(order_total_usd) AS total_value,
    COUNT(*) AS line_count
FROM {{ ref('stg_orders') }}
GROUP BY order_id, customer_id, order_month