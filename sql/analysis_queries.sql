-- Basic conversion by variant (sums)
SELECT
  variant,
  SUM(purchase) AS total_purchases,
  SUM(reach) AS total_reach,
  ROUND(1.0 * SUM(purchase) / NULLIF(SUM(reach),0), 6) AS conversion_rate
FROM marketing_ab
GROUP BY variant;

-- Per-row average conversion rate by variant
SELECT
  variant,
  COUNT(*) as rows,
  ROUND(AVG(conversion_rate), 6) AS avg_conversion_rate,
  ROUND(STDDEV(conversion_rate), 6) AS stddev_conversion_rate
FROM marketing_ab
GROUP BY variant;

-- Funnel averages
SELECT
  variant,
  ROUND(AVG(website_clicks), 3) AS avg_website_clicks,
  ROUND(AVG(add_to_cart), 3) AS avg_add_to_cart,
  ROUND(AVG(purchase), 3) AS avg_purchase
FROM marketing_ab
GROUP BY variant;
