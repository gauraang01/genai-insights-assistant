SELECT
    sku,
    product_name,
    product_id,
    stock_level,
    reorder_point,
    reorder_needed
FROM {{ source('raw', 'raw_inventory') }}
