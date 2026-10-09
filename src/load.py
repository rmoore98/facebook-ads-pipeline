"""Load: upload the three processed tables to BigQuery.
Run from the project folder: python src/load.py
"""
import os

from google.cloud import bigquery

# Uses my project by default; set GCP_PROJECT_ID to use your own
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "facebook-ads-pipeline-510822")
DATASET_ID = "facebook_ads"
PROCESSED_DIR = "data/processed"

# Explicit column types, so BigQuery never has to guess
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


def load_table(client, table_name):
    """Upload one CSV, replacing the table if it already exists."""
    path = f"{PROCESSED_DIR}/{table_name}.csv"
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # skip the header row
        schema=SCHEMAS[table_name],
        # Replace rather than append, so rerunning never creates duplicates
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with open(path, "rb") as f:
        job = client.load_table_from_file(f, table_id, job_config=job_config)
    job.result()  # wait for the upload to finish; raises an error if it failed

    table = client.get_table(table_id)
    print(f"Loaded {table_id}: {table.num_rows} rows")


def main():
    client = bigquery.Client(project=PROJECT_ID)
    for table_name in SCHEMAS:
        load_table(client, table_name)
    print("All tables loaded")


if __name__ == "__main__":
    main()