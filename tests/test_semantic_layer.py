from semantic import semantic_builder

def test_merge_semantic_with_dbt():
    dummy_dbt = {"fct_orders": {"schema": "public", "columns": {"order_id": "Order ID"}}}
    semantic = {"entities": {"orders": {"model": "fct_orders"}}, "metrics": {}, "dimensions": {}}
    merged = semantic_builder.merge_semantic_with_dbt(semantic, dummy_dbt)
    assert "orders" in merged["entities"]
    assert merged["entities"]["orders"]["schema"] == "public"
