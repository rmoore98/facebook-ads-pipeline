"""Transform: clean the raw Facebook ads CSV and split it into star schema tables."""
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "KAG_conversion_data.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

COLUMN_NAMES = {
    "ad_id": "ad_id",
    "xyz_campaign_id": "campaign_id",
    "fb_campaign_id": "ad_set_id",
    "age": "age_group",
    "gender": "gender",
    "interest": "interest_code",
    "Impressions": "impressions",
    "Clicks": "clicks",
    "Spent": "spend",
    "Total_Conversion": "total_conversions",
    "Approved_Conversion": "approved_conversions",
}


def load_raw(path: Path = RAW_FILE) -> pd.DataFrame:
    """Read the raw CSV without modifying the original file."""
    df = pd.read_csv(path)
    log.info("Loaded %d rows from %s", len(df), path.name)
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to consistent snake_case names."""
    return df.rename(columns=COLUMN_NAMES)


def build_dim_campaign(df: pd.DataFrame) -> pd.DataFrame:
    """One row per campaign."""
    return df[["campaign_id"]].drop_duplicates().sort_values("campaign_id").reset_index(drop=True)


def build_dim_ad_set(df: pd.DataFrame) -> pd.DataFrame:
    """One row per ad set, with its audience targeting."""
    cols = ["ad_set_id", "campaign_id", "age_group", "gender", "interest_code"]
    return df[cols].drop_duplicates().sort_values("ad_set_id").reset_index(drop=True)


def build_fact_ad_performance(df: pd.DataFrame) -> pd.DataFrame:
    """One row per ad, with its performance numbers."""
    cols = ["ad_id", "ad_set_id", "impressions", "clicks", "spend",
            "total_conversions", "approved_conversions"]
    fact = df[cols].sort_values("ad_id").reset_index(drop=True)
    fact["spend"] = fact["spend"].round(2)  # raw values have float noise, e.g. 1.429999948
    return fact


def run_quality_checks(raw: pd.DataFrame, dim_campaign: pd.DataFrame,
                       dim_ad_set: pd.DataFrame, fact: pd.DataFrame) -> None:
    """Stop the pipeline loudly if any assumption about the data is broken."""
    checks = {
        "no missing values in raw data": raw.notna().all().all(),
        "ad_id is unique": fact["ad_id"].is_unique,
        "ad_set_id is unique in dim_ad_set": dim_ad_set["ad_set_id"].is_unique,
        "campaign_id is unique in dim_campaign": dim_campaign["campaign_id"].is_unique,
        "clicks never exceed impressions": (fact["clicks"] <= fact["impressions"]).all(),
        "approved never exceeds total conversions":
            (fact["approved_conversions"] <= fact["total_conversions"]).all(),
        "spend is zero exactly when clicks are zero":
            ((fact["spend"] == 0) == (fact["clicks"] == 0)).all(),
        "joining tables back keeps every ad exactly once":
            len(fact.merge(dim_ad_set, on="ad_set_id")) == len(raw),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Quality checks failed: {failed}")
    log.info("All %d quality checks passed", len(checks))


def save_tables(tables: dict[str, pd.DataFrame], out_dir: Path = PROCESSED_DIR) -> None:
    """Write each table to its own CSV in data/processed."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        path = out_dir / f"{name}.csv"
        table.to_csv(path, index=False)
        log.info("Saved %s (%d rows)", path.name, len(table))


def main() -> None:
    raw = standardize_columns(load_raw())
    dim_campaign = build_dim_campaign(raw)
    dim_ad_set = build_dim_ad_set(raw)
    fact = build_fact_ad_performance(raw)
    run_quality_checks(raw, dim_campaign, dim_ad_set, fact)
    save_tables({
        "dim_campaign": dim_campaign,
        "dim_ad_set": dim_ad_set,
        "fact_ad_performance": fact,
    })


if __name__ == "__main__":
    main()
