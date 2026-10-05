SELECT blob1 AS page, blob2 AS device,
       quantileExactWeighted(0.75)(double1, _sample_interval) AS lcp_p75,
       SUM(if(blob6 = 'good', _sample_interval, 0)) / SUM(_sample_interval) AS lcp_share_good,
       SUM(_sample_interval) AS samples
FROM site_rum
WHERE double1 >= 0 AND timestamp > NOW() - INTERVAL '28' DAY
GROUP BY page, device
HAVING samples >= 50
ORDER BY samples DESC;

SELECT blob1 AS page, blob2 AS device,
       quantileExactWeighted(0.75)(double2, _sample_interval) AS inp_p75,
       SUM(_sample_interval) AS samples
FROM site_rum
WHERE double2 >= 0 AND timestamp > NOW() - INTERVAL '28' DAY
GROUP BY page, device
HAVING samples >= 50
ORDER BY samples DESC;

SELECT blob1 AS page, blob2 AS device,
       quantileExactWeighted(0.75)(double3, _sample_interval) AS cls_p75,
       SUM(_sample_interval) AS samples
FROM site_rum
WHERE double3 >= 0 AND timestamp > NOW() - INTERVAL '28' DAY
GROUP BY page, device
HAVING samples >= 50
ORDER BY samples DESC;

SELECT blob1 AS page,
       quantileExactWeighted(0.75)(double6, _sample_interval) AS ttfb,
       quantileExactWeighted(0.75)(double7, _sample_interval) AS resource_load_delay,
       quantileExactWeighted(0.75)(double8, _sample_interval) AS resource_load_duration,
       quantileExactWeighted(0.75)(double9, _sample_interval) AS element_render_delay,
       SUM(_sample_interval) AS samples
FROM site_rum
WHERE double1 >= 0 AND blob2 = 'mobile' AND timestamp > NOW() - INTERVAL '28' DAY
GROUP BY page
HAVING samples >= 50
ORDER BY samples DESC;

SELECT blob10 AS target, blob1 AS page,
       quantileExactWeighted(0.75)(double2, _sample_interval) AS inp_p75,
       quantileExactWeighted(0.75)(double10, _sample_interval) AS input_delay,
       quantileExactWeighted(0.75)(double11, _sample_interval) AS processing,
       quantileExactWeighted(0.75)(double12, _sample_interval) AS presentation_delay,
       SUM(_sample_interval) AS samples
FROM site_rum
WHERE double2 >= 0 AND timestamp > NOW() - INTERVAL '28' DAY
GROUP BY target, page
HAVING samples >= 20
ORDER BY inp_p75 DESC
LIMIT 20;

SELECT blob5 AS build, blob2 AS device,
       quantileExactWeighted(0.75)(double1, _sample_interval) AS lcp_p75,
       quantileExactWeighted(0.75)(double2, _sample_interval) AS inp_p75,
       SUM(_sample_interval) AS samples
FROM site_rum
WHERE timestamp > NOW() - INTERVAL '14' DAY
GROUP BY build, device
HAVING samples >= 100
ORDER BY build DESC;
