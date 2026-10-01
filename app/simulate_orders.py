"""
simulate_orders.py

Simulates a real-time retail order feed from a static Kaggle CSV dataset
(the "Sales Records" dataset: Region, Country, Item Type, Sales Channel,
Order Priority, Order Date, Order ID, Ship Date, Units Sold, Unit Price,
Unit Cost, Total Revenue, Total Cost, Total Profit).

What it does:
1. Uploads the raw CSV to S3 once (raw data archive).
2. Replays the dataset row by row, writing each row into DynamoDB with a
   fresh timestamp, at a configurable interval, to mimic orders arriving
   live. The dashboard (dashboard.py) reads from DynamoDB and redraws.

Usage:
    python simulate_orders.py --interval 1.5 --loop
    python simulate_orders.py --csv "../data/50000 Sales Records.csv" --profile terraform --loop

Environment variables (or edit the DEFAULTS below):
    AWS_REGION            default: ap-south-1
    S3_BUCKET             default: retail-analytics-raw-data-sanket-jadhav
    DYNAMODB_TABLE        default: retail_live_orders
"""

import argparse
import csv
import os
import random
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3

# ---------------- Config ----------------
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "retail-analytics-raw-data-sanket-jadhav")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "retail_live_orders")

# Resolves to <project_root>/data/50000 Sales Records.csv regardless of the
# directory you run this script from (matches the iac-project/data/ layout).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "data", "50000 Sales Records.csv")

# Maps the dataset's human-readable column names to the snake_case
# attribute names stored in DynamoDB.
COLUMN_MAP = {
    "Region": "region",
    "Country": "country",
    "Item Type": "item_type",
    "Sales Channel": "sales_channel",
    "Order Priority": "order_priority",
    "Order Date": "order_date",
    "Order ID": "source_order_id",
    "Ship Date": "ship_date",
    "Units Sold": "units_sold",
    "Unit Price": "unit_price",
    "Unit Cost": "unit_cost",
    "Total Revenue": "total_revenue",
    "Total Cost": "total_cost",
    "Total Profit": "total_profit",
}

NUMERIC_FIELDS = {
    "units_sold", "unit_price", "unit_cost",
    "total_revenue", "total_cost", "total_profit",
}


def upload_raw_csv(s3_client, csv_path: str):
    """Archive the raw dataset in S3 (satisfies the 'raw storage' piece)."""
    key = f"raw/{os.path.basename(csv_path)}"
    print(f"Uploading {csv_path} to s3://{S3_BUCKET}/{key} ...")
    try:
        s3_client.upload_file(csv_path, S3_BUCKET, key)
        print("Upload complete.")
    except Exception as e:
        print(f"Warning: could not upload raw CSV to S3 ({e}). Continuing with simulation anyway.")


def to_dynamo_item(row: dict) -> dict:
    """Convert one CSV row into a DynamoDB item with a unique key."""
    item = {}
    for csv_col, attr in COLUMN_MAP.items():
        value = row.get(csv_col, "")
        if attr in NUMERIC_FIELDS:
            try:
                value = Decimal(str(value))
            except (TypeError, ValueError):
                value = Decimal("0")
        item[attr] = value

    # Unique partition key: the source Order ID isn't guaranteed unique
    # across repeated loops of the file, so pair it with a short UUID.
    item["order_id"] = f"{item.get('source_order_id', 'unknown')}-{uuid.uuid4().hex[:8]}"
    # Timestamp of when THIS simulated order "arrived" — this is what makes
    # it look live, since the dataset's own Order Date is static/historical.
    item["ingested_at"] = datetime.now(timezone.utc).isoformat()
    return item


def run_simulation(csv_path: str, interval: float, jitter: float, loop: bool, profile: str = None, limit: int = None):
    session = boto3.Session(profile_name=profile, region_name=AWS_REGION)
    s3 = session.client("s3")
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(DYNAMODB_TABLE)

    upload_raw_csv(s3, csv_path)

    pass_number = 0
    while True:
        pass_number += 1
        print(f"--- Starting simulation pass {pass_number} ---")
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if limit is not None and count >= limit:
                    print(f"  Reached --limit {limit}, stopping this pass early.")
                    break

                item = to_dynamo_item(row)
                try:
                    table.put_item(Item=item)
                    count += 1
                    if count % 25 == 0:
                        print(f"  Inserted {count} orders so far this pass...")
                except Exception as e:
                    print(f"  Error inserting row: {e}")

                sleep_time = max(0.0, interval + random.uniform(-jitter, jitter))
                time.sleep(sleep_time)

        print(f"--- Pass {pass_number} complete: {count} orders inserted ---")
        if not loop:
            break


def main():
    parser = argparse.ArgumentParser(description="Simulate a live retail order feed into DynamoDB.")
    parser.add_argument("--csv", default=DEFAULT_CSV_PATH, help="Path to the Kaggle CSV file (default: ../data/50000 Sales Records.csv relative to this script).")
    parser.add_argument("--interval", type=float, default=1.5, help="Seconds between simulated orders.")
    parser.add_argument("--jitter", type=float, default=0.5, help="Random +/- seconds added to interval.")
    parser.add_argument("--loop", action="store_true", help="Replay the dataset forever instead of stopping at the end.")
    parser.add_argument("--profile", default=None, help="AWS CLI profile to use (e.g. 'terraform'). Default: whatever 'aws login'/default credentials resolve to.")
    parser.add_argument("--limit", type=int, default=None, help="Only replay the first N rows per pass.")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit(
            f"Could not find '{args.csv}'. Download the dataset from Kaggle and place it in the data/ folder, "
            f"or pass --csv \"path/to/file.csv\""
        )

    run_simulation(
    args.csv,
    args.interval,
    args.jitter,
    args.loop,
    profile=args.profile,
    limit=args.limit
    )


if __name__ == "__main__":
    main()