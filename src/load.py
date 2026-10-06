"""Load: upload the processed star schema tables to BigQuery."""
import logging
import os
from pathlib import Path

from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "facebook-ads-pipeline-510822")
DATASET_ID = "facebook_ads"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

# Explicit schemas, so BigQuery never has to guess column types.
SCHEMAS = {
    "dim_campaign": [
        bigquery.SchemaField("campaign_id", "INT64", mode="REQUIRED"),
    ],
    "dim_ad_set": [
        bigquery.SchemaField("ad_set_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("campaign_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("age_group", "STRING"),
        bigquery.SchemaField("gender", "STRING"),
        bigquery.SchemaField("interest_code", "INT64"),
    ],
    "fact_ad_performance": [
        bigquery.SchemaField("ad_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("ad_set_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("impressions", "INT64"),
        bigquery.SchemaField("clicks", "INT64"),
        bigquery.SchemaField("spend", "NUMERIC"),
        bigquery.SchemaField("total_conversions", "INT64"),
        bigquery.SchemaField("approved_conversions", "INT64"),
    ],
}


def load_table(client: bigquery.Client, table_name: str) -> None:
    """Upload one CSV, replacing the table if it already exists."""
    path = PROCESSED_DIR / f"{table_name}.csv"
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=SCHEMAS[table_name],
        # Replace rather than append, so rerunning never creates duplicates.
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    with open(path, "rb") as f:
        job = client.load_table_from_file(f, table_ref, job_config=job_config)
    job.result()  # wait for the upload to finish; raises an error if it failed

    loaded = client.get_table(table_ref).num_rows
    log.info("Loaded %s: %d rows", table_ref, loaded)


def main() -> None:
    client = bigquery.Client(project=PROJECT_ID)
    for table_name in SCHEMAS:
        load_table(client, table_name)
    log.info("All tables loaded into %s.%s", PROJECT_ID, DATASET_ID)


if __name__ == "__main__":
    main()
