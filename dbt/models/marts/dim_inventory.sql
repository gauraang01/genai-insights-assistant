SELECT
    sku,
    product_name,
    stock_level,
    reorder_point,
    reorder_needed
FROM {{ ref('stg_inventory') }}
