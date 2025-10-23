WITH base AS (
    SELECT * FROM {{ source('raw', 'raw_orders') }}
),
ship AS (
    SELECT * FROM {{ source('raw', 'raw_shipments') }}
)
SELECT
    o.order_id,
    o.customer_id,
    o.product_id,
    o.order_date,
    o.order_month,
    -- ETL uses 'order_total_usd' (we alias to total_value for consistency)
    o.order_total_usd AS total_value,
    s.status AS shipment_status
FROM base o
LEFT JOIN ship s ON o.order_id = s.order_id
