-- Performance by audience segment: 
-- Which age and gender groups convert most cheaply?

SELECT
  s.age_group,
  s.gender,
  COUNT(*) AS ads,
  SUM(f.spend) AS spend,
  SUM(f.approved_conversions) AS approved_conversions,
  ROUND(SAFE_DIVIDE(SUM(f.clicks), SUM(f.impressions)) * 100, 3) AS ctr_pct,
  ROUND(SAFE_DIVIDE(SUM(f.spend), SUM(f.approved_conversions)), 2) AS cost_per_approved
FROM `facebook-ads-pipeline-510822.facebook_ads.fact_ad_performance` AS f
JOIN `facebook-ads-pipeline-510822.facebook_ads.dim_ad_set` AS s
  ON f.ad_set_id = s.ad_set_id
GROUP BY s.age_group, s.gender
ORDER BY cost_per_approved;
