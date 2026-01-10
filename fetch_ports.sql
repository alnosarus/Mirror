INSTALL spatial;
LOAD spatial;

COPY (
  SELECT
    id,
    names.primary as name,
    categories.primary as category,
    confidence,
    geometry
  FROM read_parquet('s3://overturemaps-us-west-2/release/2025-12-17.0/theme=places/type=place/*', filename=true, hive_partitioning=1)
  WHERE (
    categories.primary = 'port' OR
    categories.primary = 'marina' OR
    categories.primary = 'harbor'
  )
  AND bbox.xmin BETWEEN -118.7 AND -118.15
  AND bbox.ymin BETWEEN 33.7 AND 34.35
) TO 'la_ports.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');
