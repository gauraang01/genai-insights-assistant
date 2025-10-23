# scripts/ge_checks.py
import os
import pandas as pd

DATA_DIR = os.getenv("DATA_DIR", "data")

def check_orders(df: pd.DataFrame):
    """Validate orders dataset."""
    expected_cols = {"order_id", "customer_id", "product_id", "order_date", "total_value"}
    missing = expected_cols - set(df.columns)
    assert not missing, f"Missing columns in orders.csv: {missing}"

    # Unique order IDs
    assert df["order_id"].is_unique, "order_id values are not unique"

    # No null totals or dates
    assert df["total_value"].notnull().all(), "Null values found in total_value"
    assert pd.to_datetime(df["order_date"], errors="coerce").notnull().all(), "Invalid order_date values"

    # Numeric type check
    assert pd.api.types.is_numeric_dtype(df["total_value"]), "total_value not numeric"

def check_shipments(df: pd.DataFrame):
    """Validate shipments dataset."""
    expected_cols = {"shipment_id", "order_id", "shipped_date", "carrier", "tracking_number", "status"}
    missing = expected_cols - set(df.columns)
    assert not missing, f"Missing columns in shipments.csv: {missing}"

    assert df["shipment_id"].is_unique, "shipment_id values are not unique"

    allowed = {"delivered", "in_transit", "pending"}
    unknown = set(df["status"].dropna().unique()) - allowed
    if unknown:
        print(f"⚠️ Warning: shipments.status contains unknown values: {unknown}")

    # Validate shipped_date
    assert pd.to_datetime(df["shipped_date"], errors="coerce").notnull().all(), "Invalid shipped_date format"

def check_inventory(df: pd.DataFrame):
    """Validate inventory dataset."""
    expected_cols = {"sku", "product_name", "stock_level", "reorder_point"}
    missing = expected_cols - set(df.columns)
    assert not missing, f"Missing columns in inventory.csv: {missing}"

    assert pd.api.types.is_numeric_dtype(df["stock_level"]), "stock_level must be numeric"
    assert (df["stock_level"] >= 0).all(), "Negative stock_level values found"

    assert pd.api.types.is_numeric_dtype(df["reorder_point"]), "reorder_point must be numeric"
    assert (df["reorder_point"] >= 0).all(), "Negative reorder_point values found"

def run_checks():
    """Run all validation checks."""
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    shipments = pd.read_csv(os.path.join(DATA_DIR, "shipments.csv"))
    inventory = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))

    check_orders(orders)
    check_shipments(shipments)
    check_inventory(inventory)
    print("All Great Expectations-style checks passed successfully!")

if __name__ == "__main__":
    run_checks()
