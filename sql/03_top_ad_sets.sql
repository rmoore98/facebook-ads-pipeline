-- Top ad sets:
-- Which ad sets have the lowest cost per purchase?

-- Totals per ad set
WITH ad_set_totals AS (
  SELECT
    s.campaign_id,
    s.ad_set_id,
    s.age_group,
    s.gender,
    s.interest_code,
    SUM(f.spend) AS spend,
    SUM(f.approved_conversions) AS approved_conversions
  FROM `facebook-ads-pipeline-510822.facebook_ads.fact_ad_performance` AS f
  JOIN `facebook-ads-pipeline-510822.facebook_ads.dim_ad_set` AS s
    ON f.ad_set_id = s.ad_set_id
  GROUP BY s.campaign_id, s.ad_set_id, s.age_group, s.gender, s.interest_code
  -- Ad sets with only 1-4 purchases can rank high by luck, so require at least 5
  HAVING SUM(f.approved_conversions) >= 5
)

-- Cheapest cost per purchase
SELECT
  campaign_id,
  ad_set_id,
  age_group,
  gender,
  interest_code,
  spend,
  approved_conversions,
  ROUND(spend / approved_conversions, 2) AS cost_per_approved
FROM ad_set_totals
ORDER BY cost_per_approved
LIMIT 10;