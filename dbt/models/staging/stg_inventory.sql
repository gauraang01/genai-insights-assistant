SELECT
    sku,
    product_name,
    stock_level,
    reorder_point,
    reorder_needed
FROM {{ source('raw', 'raw_inventory') }}
