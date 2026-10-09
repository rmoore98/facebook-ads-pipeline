-- Funnel performance by campaign:
-- Which campaign has the lowest cost per purchase?

-- Totals per campaign
WITH campaign_totals AS (
  SELECT
    s.campaign_id,
    SUM(f.impressions) AS impressions,
    SUM(f.clicks) AS clicks,
    SUM(f.spend) AS spend,
    SUM(f.approved_conversions) AS approved_conversions
  FROM `facebook-ads-pipeline-510822.facebook_ads.fact_ad_performance` AS f
  JOIN `facebook-ads-pipeline-510822.facebook_ads.dim_ad_set` AS s
    ON f.ad_set_id = s.ad_set_id
  GROUP BY s.campaign_id
),

-- Total spend for all campaigns, used to calculate each campaign's share
grand_totals AS (
  SELECT SUM(spend) AS total_spend
  FROM campaign_totals
)

-- Rates and shares per campaign
SELECT
  campaign_id,
  impressions,
  clicks,
  spend,
  approved_conversions,
  ROUND(clicks / impressions * 100, 3) AS ctr_pct,
  ROUND(spend / clicks, 2) AS cost_per_click,
  ROUND(spend / approved_conversions, 2) AS cost_per_approved,
  -- Purchases per 1,000 impressions, since some purchases happen without a click
  ROUND(approved_conversions / impressions * 1000, 4) AS approved_per_1k_impr,
  ROUND(spend / total_spend * 100, 1) AS pct_of_total_spend
FROM campaign_totals
CROSS JOIN grand_totals
ORDER BY cost_per_approved;
