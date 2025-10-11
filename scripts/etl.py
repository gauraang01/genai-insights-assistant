# scripts/etl.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("etl")

# Config from env
PG_USER = os.getenv("POSTGRES_USER", "genai")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "changeme")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "genai_db")

DATA_DIR = os.getenv("DATA_DIR", "data")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def pg_engine():
    url = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    return create_engine(url, echo=False)

def read_csvs():
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"), parse_dates=["order_date"])
    shipments = pd.read_csv(os.path.join(DATA_DIR, "shipments.csv"), parse_dates=["shipped_date"])
    inventory = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))
    return orders, shipments, inventory

def transform(orders, shipments, inventory):
    # example transforms
    orders["order_month"] = orders["order_date"].dt.to_period("M").astype(str)
    orders["order_total_usd"] = orders["order_total"]  # placeholder if currency conversions
    shipments_small = shipments[["shipment_id", "order_id", "shipped_date", "status", "carrier"]]
    # simple join: attach whether an order has a shipment
    orders_ship = orders.merge(shipments_small.groupby("order_id")["status"].last().reset_index(),
                               on="order_id", how="left")
    # inventory low-stock flag
    inventory["reorder_needed"] = inventory["stock_level"] <= inventory["reorder_point"]
    return orders, shipments_small, inventory, orders_ship

def load_to_postgres(df, table_name, engine):
    logger.info(f"Loading {len(df)} rows into {table_name}")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    logger.info("Load complete")

def save_outputs(orders_ship, output_dir=OUTPUT_DIR):
    agg = orders_ship.groupby("order_month").agg(
        orders_count=("order_id", "count"),
        total_revenue=("order_total_usd", "sum")
    ).reset_index()
    out_path = os.path.join(output_dir, f"orders_by_month_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    agg.to_csv(out_path, index=False)
    logger.info(f"Wrote aggregated output {out_path}")
    return out_path, agg

def run_etl():
    logger.info("ETL start")
    engine = pg_engine()
    orders, shipments, inventory = read_csvs()
    orders, shipments_small, inventory, orders_ship = transform(orders, shipments, inventory)

    # load staging tables
    load_to_postgres(orders, "raw_orders", engine)
    load_to_postgres(shipments_small, "raw_shipments", engine)
    load_to_postgres(inventory, "raw_inventory", engine)


    out_path, agg = save_outputs(orders_ship)
    logger.info("ETL finished")
    return {"output_path": out_path, "agg_preview": agg.to_dict(orient="records")}

if __name__ == "__main__":
    res = run_etl()
    print("ETL result:", res)
