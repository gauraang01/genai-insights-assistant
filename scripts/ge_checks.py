# scripts/ge_checks.py
import os
import pandas as pd

DATA_DIR = os.getenv("DATA_DIR", "data")

def check_orders(df: pd.DataFrame):
    # Ensure columns exist
    assert "order_id" in df.columns, "Missing column: order_id"
    assert "order_total" in df.columns, "Missing column: order_total"
    assert "order_date" in df.columns, "Missing column: order_date"

    # Unique order IDs
    assert df["order_id"].is_unique, "order_id values are not unique"

    # No null totals or dates
    assert df["order_total"].notnull().all(), "Null values found in order_total"
    assert pd.to_datetime(df["order_date"], errors="coerce").notnull().all(), "Invalid order_date values"

def check_shipments(df: pd.DataFrame):
    assert "shipment_id" in df.columns, "Missing column: shipment_id"
    assert df["shipment_id"].is_unique, "shipment_id values are not unique"

    allowed = {"delivered", "in_transit", "pending"}
    unknown = set(df["status"].dropna().unique()) - allowed
    if unknown:
        print(f"⚠️  Warning: shipments.status contains unknown values: {unknown}")

def check_inventory(df: pd.DataFrame):
    assert "sku" in df.columns, "Missing column: sku"
    assert "stock_level" in df.columns, "Missing column: stock_level"
    assert "reorder_point" in df.columns, "Missing column: reorder_point"

    # Numeric and non-negative checks
    assert pd.api.types.is_numeric_dtype(df["stock_level"]), "stock_level not numeric"
    assert (df["stock_level"] >= 0).all(), "Negative stock_level values found"

def run_checks():
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    shipments = pd.read_csv(os.path.join(DATA_DIR, "shipments.csv"))
    inventory = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))

    check_orders(orders)
    check_shipments(shipments)
    check_inventory(inventory)
    print("All Great Expectations checks passed successfully!")

if __name__ == "__main__":
    run_checks()
