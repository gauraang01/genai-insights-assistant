WITH base AS (
    SELECT * FROM {{ source('raw', 'raw_orders') }}
),
ship AS (
    SELECT * FROM {{ source('raw', 'raw_shipments') }}
)
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_total,
    o.currency,
    o.order_month,
    o.order_total_usd,
    s.status AS shipment_status
FROM base o
LEFT JOIN ship s ON o.order_id = s.order_id
