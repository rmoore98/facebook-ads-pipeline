-- Top 3 ad sets per campaign by cost per approved conversion

WITH ad_set_stats AS (
  SELECT
    s.campaign_id,
    s.ad_set_id,
    s.age_group,
    s.gender,
    s.interest_code,
    SUM(f.spend) AS spend,
    SUM(f.approved_conversions) AS approved_conversions,
    SAFE_DIVIDE(SUM(f.spend), SUM(f.approved_conversions)) AS cost_per_approved
  FROM `facebook-ads-pipeline-510822.facebook_ads.fact_ad_performance` AS f
  JOIN `facebook-ads-pipeline-510822.facebook_ads.dim_ad_set` AS s
    ON f.ad_set_id = s.ad_set_id
  GROUP BY s.campaign_id, s.ad_set_id, s.age_group, s.gender, s.interest_code
  -- Prevent small ad sets from top ranks (skewed data)
  HAVING SUM(f.approved_conversions) > 0 AND SUM(f.spend) >= 10)

  
SELECT
  campaign_id,
  RANK() OVER (PARTITION BY campaign_id ORDER BY cost_per_approved) AS rank_in_campaign,
  ad_set_id,
  age_group,
  gender,
  interest_code,
  spend,
  approved_conversions,
  ROUND(cost_per_approved, 2) AS cost_per_approved
FROM ad_set_stats
QUALIFY rank_in_campaign <= 3
ORDER BY campaign_id, rank_in_campaign;
