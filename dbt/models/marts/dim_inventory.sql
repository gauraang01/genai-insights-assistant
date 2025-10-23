SELECT
    sku,
    product_id,
    product_name,
    stock_level,
    reorder_point,
    reorder_needed
FROM {{ ref('stg_inventory') }}
