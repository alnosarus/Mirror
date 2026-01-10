INSTALL spatial;
LOAD spatial;

-- Fetch airport infrastructure
COPY (
  SELECT
    id,
    names.primary as name,
    subtype,
    class,
    geometry
  FROM read_parquet('s3://overturemaps-us-west-2/release/2025-12-17.0/theme=base/type=infrastructure/*', filename=true, hive_partitioning=1)
  WHERE subtype = 'airport'
  AND bbox.xmin BETWEEN -118.7 AND -118.15
  AND bbox.ymin BETWEEN 33.7 AND 34.35
) TO 'la_airport_infrastructure.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');

-- Fetch port/pier infrastructure
COPY (
  SELECT
    id,
    names.primary as name,
    subtype,
    class,
    geometry
  FROM read_parquet('s3://overturemaps-us-west-2/release/2025-12-17.0/theme=base/type=infrastructure/*', filename=true, hive_partitioning=1)
  WHERE (subtype = 'pier' OR subtype = 'quay')
  AND bbox.xmin BETWEEN -118.7 AND -118.15
  AND bbox.ymin BETWEEN 33.7 AND 34.35
) TO 'la_port_infrastructure.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');
