WITH orders AS (
    SELECT
        order_id,
        product_id,
        order_date,
        total_value
    FROM {{ ref('stg_orders') }}
),
shipments AS (
    SELECT
        order_id,
        shipped_date
    FROM {{ ref('stg_shipments') }}
)
SELECT
    o.product_id,
    DATE_TRUNC('month', o.order_date)::date AS order_month,
    SUM(o.total_value) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders,
    AVG(DATE_PART('day', s.shipped_date - o.order_date)) AS avg_shipment_delay
FROM orders o
LEFT JOIN shipments s USING (order_id)
GROUP BY o.product_id, order_month
