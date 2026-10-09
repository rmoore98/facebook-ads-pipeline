"""Transform: clean the raw Facebook ads CSV and split it into three tables
(campaigns, ad sets, and ads), then check the data before saving.
Run from the project folder: python src/transform.py
"""
import pandas as pd

RAW_FILE = "data/raw/KAG_conversion_data.csv"
PROCESSED_DIR = "data/processed"

# Rename columns to lowercase names that say what each column really is
COLUMN_NAMES = {
    "xyz_campaign_id": "campaign_id",
    "fb_campaign_id": "ad_set_id",  # works like an ad set, not a campaign (see notebook)
    "age": "age_group",
    "interest": "interest_code",
    "Impressions": "impressions",
    "Clicks": "clicks",
    "Spent": "spend",
    "Total_Conversion": "total_conversions",
    "Approved_Conversion": "approved_conversions",
}


def build_dim_campaign(df):
    """One row per campaign."""
    dim_campaign = df[["campaign_id"]].drop_duplicates()
    dim_campaign = dim_campaign.sort_values("campaign_id")
    return dim_campaign


def build_dim_ad_set(df):
    """One row per ad set, with its audience targeting."""
    cols = ["ad_set_id", "campaign_id", "age_group", "gender", "interest_code"]
    dim_ad_set = df[cols].drop_duplicates()
    dim_ad_set = dim_ad_set.sort_values("ad_set_id")
    return dim_ad_set


def build_fact_ad_performance(df):
    """One row per ad, with its performance numbers."""
    cols = ["ad_id", "ad_set_id", "impressions", "clicks", "spend",
            "total_conversions", "approved_conversions"]
    fact = df[cols].sort_values("ad_id")
    # Raw spend has tiny float errors (e.g. 1.429999948), so round to cents
    fact["spend"] = fact["spend"].round(2)
    return fact


def run_quality_checks(raw, dim_campaign, dim_ad_set, fact):
    """Stop the pipeline if any assumption about the data is wrong."""
    problems = []

    if raw.isnull().sum().sum() > 0:
        problems.append("raw data has missing values")

    if fact["ad_id"].nunique() != len(fact):
        problems.append("ad_id is not unique")

    # If an ad set targeted more than one audience, its ID would appear twice here
    if dim_ad_set["ad_set_id"].nunique() != len(dim_ad_set):
        problems.append("ad_set_id is not unique in dim_ad_set")

    if dim_campaign["campaign_id"].nunique() != len(dim_campaign):
        problems.append("campaign_id is not unique in dim_campaign")

    if (fact["clicks"] > fact["impressions"]).any():
        problems.append("some ads have more clicks than impressions")

    if (fact["approved_conversions"] > fact["total_conversions"]).any():
        problems.append("some ads have more approved than total conversions")

    # Ads seem to be paid per click, so spend should be zero exactly when clicks are zero
    zero_clicks = fact["clicks"] == 0
    zero_spend = fact["spend"] == 0
    if (zero_clicks != zero_spend).any():
        problems.append("zero spend and zero clicks don't line up")

    # Joining ads to their ad sets should give back one row per ad
    joined = fact.merge(dim_ad_set, on="ad_set_id")
    if len(joined) != len(raw):
        problems.append("joining fact to dim_ad_set changed the number of rows")

    if problems:
        raise ValueError(f"Quality checks failed: {problems}")
    print("All 8 quality checks passed")


def save_tables(dim_campaign, dim_ad_set, fact):
    """Write each table to its own CSV in data/processed."""
    dim_campaign.to_csv(f"{PROCESSED_DIR}/dim_campaign.csv", index=False)
    dim_ad_set.to_csv(f"{PROCESSED_DIR}/dim_ad_set.csv", index=False)
    fact.to_csv(f"{PROCESSED_DIR}/fact_ad_performance.csv", index=False)
    print(f"Saved dim_campaign ({len(dim_campaign)} rows), "
          f"dim_ad_set ({len(dim_ad_set)} rows), "
          f"fact_ad_performance ({len(fact)} rows)")


def main():
    raw = pd.read_csv(RAW_FILE)
    print(f"Loaded {len(raw)} rows from {RAW_FILE}")
    raw = raw.rename(columns=COLUMN_NAMES)

    dim_campaign = build_dim_campaign(raw)
    dim_ad_set = build_dim_ad_set(raw)
    fact = build_fact_ad_performance(raw)

    run_quality_checks(raw, dim_campaign, dim_ad_set, fact)
    save_tables(dim_campaign, dim_ad_set, fact)


if __name__ == "__main__":
    main()