-- Funnel performance by campaign: 
-- Which campaign is best at turning spend into purchases?

SELECT
  s.campaign_id,
  SUM(f.impressions) AS impressions,
  SUM(f.clicks) AS clicks,
  SUM(f.spend) AS spend,
  SUM(f.approved_conversions) AS approved_conversions,
  ROUND(SAFE_DIVIDE(SUM(f.clicks), SUM(f.impressions)) * 100, 3) AS ctr_pct,
  ROUND(SAFE_DIVIDE(SUM(f.spend), SUM(f.clicks)), 2) AS cost_per_click,
  ROUND(SAFE_DIVIDE(SUM(f.spend), SUM(f.approved_conversions)), 2) AS cost_per_approved,
  -- Conversions per 1,000 impressions, since some conversions happen without a click
  ROUND(SAFE_DIVIDE(SUM(f.approved_conversions), SUM(f.impressions)) * 1000, 4) AS approved_per_1k_impr,
  -- Each campaign's share of total spend (window function over the grouped rows)
  ROUND(SUM(f.spend) / SUM(SUM(f.spend)) OVER () * 100, 1) AS pct_of_total_spend
FROM `facebook-ads-pipeline-510822.facebook_ads.fact_ad_performance` AS f
JOIN `facebook-ads-pipeline-510822.facebook_ads.dim_ad_set` AS s
  ON f.ad_set_id = s.ad_set_id
GROUP BY s.campaign_id
ORDER BY spend DESC;
