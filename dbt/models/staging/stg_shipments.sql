SELECT
    shipment_id,
    order_id,
    shipped_date,
    carrier,
    status
FROM {{ source('raw', 'raw_shipments') }}
