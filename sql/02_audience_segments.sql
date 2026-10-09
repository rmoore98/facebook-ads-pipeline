-- Performance by audience segment:
-- Which age and gender groups have the lowest cost per purchase?

-- Totals for each age and gender group
WITH segment_totals AS (
  SELECT
    s.age_group,
    s.gender,
    COUNT(*) AS ads,
    SUM(f.impressions) AS impressions,
    SUM(f.clicks) AS clicks,
    SUM(f.spend) AS spend,
    SUM(f.approved_conversions) AS approved_conversions
  FROM `facebook-ads-pipeline-510822.facebook_ads.fact_ad_performance` AS f
  JOIN `facebook-ads-pipeline-510822.facebook_ads.dim_ad_set` AS s
    ON f.ad_set_id = s.ad_set_id
  GROUP BY s.age_group, s.gender
),

-- Totals for all groups, used to calculate each group's share
grand_totals AS (
  SELECT
    SUM(spend) AS total_spend,
    SUM(approved_conversions) AS total_approved
  FROM segment_totals
)

-- Rates and shares per group
SELECT
  age_group,
  gender,
  ads,
  spend,
  approved_conversions,
  ROUND(clicks / impressions * 100, 3) AS ctr_pct,
  -- Purchases per click (some purchases had no click, so this is approximate)
  ROUND(approved_conversions / clicks * 100, 1) AS conversion_rate_pct,
  ROUND(spend / total_spend * 100, 1) AS pct_of_total_spend,
  ROUND(approved_conversions / total_approved * 100, 1) AS pct_of_total_approved,
  ROUND(spend / approved_conversions, 2) AS cost_per_approved
FROM segment_totals
CROSS JOIN grand_totals
ORDER BY cost_per_approved;