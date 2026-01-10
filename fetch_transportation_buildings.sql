INSTALL spatial;
LOAD spatial;

COPY (
  SELECT
    id,
    names.primary as name,
    subtype,
    class,
    height,
    num_floors,
    geometry
  FROM read_parquet('s3://overturemaps-us-west-2/release/2025-12-17.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
  WHERE (
    subtype = 'transportation'
    OR class IN ('train_station', 'parking', 'hangar', 'transportation')
  )
  AND bbox.xmin BETWEEN -118.7 AND -118.15
  AND bbox.ymin BETWEEN 33.7 AND 34.35
) TO 'la_transportation_buildings.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');
