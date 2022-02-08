
-- Question 1
--- Creating External Table for FHV 2019 dataset
CREATE OR REPLACE EXTERNAL TABLE
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019` OPTIONS( format = 'PARQUET',
    uris = ['gs://dtc_data_lake_blissful-scout-339008/raw/fhv_tripdata_2019-*.parquet']);
    
--- and Query the Row size
SELECT COUNT(*) FROM `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;
--- Ans: 42084899


-- Question 2
--- TODO: Research that, seems like it is just approximation
SELECT
  COUNT(DISTINCT dispatching_base_num)
FROM
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;

--- Ans: 792



 
  -- Question 3
  -- dropoff_datetime, dispatching_base_num
  -- dropoff_datetime is not suitable for the partitioning as it is timestamp type and its distinct values approaximately 14529592
  -- dropoff_datetime can be used for partitioning if we are saying by DATE only as Distinct values 549
SELECT
  COUNT(DISTINCT DATE(dropoff_datetime))
FROM
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;
--
SELECT
  DATE(dropoff_datetime) AS dropoff_date,
  COUNT(DATE(dropoff_datetime)) AS counter
FROM
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`
GROUP BY
  dropoff_date
ORDER BY
  counter DESC;

  -- on the other hand we can use dispatching_base_num as distinct values are 792
SELECT
  `dispatching_base_num`,
  COUNT(dispatching_base_num) AS counter
FROM
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`
GROUP BY
  dispatching_base_num
ORDER BY
  counter DESC;

-- Create Non-partitioned Table from external table
CREATE OR REPLACE TABLE `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_non_partitioned`
AS SELECT * FROM `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;

-- Create Partitioned Table from non_partitioned table
CREATE OR REPLACE TABLE `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_Q3Q4`
PARTITION BY DATE(dropoff_datetime) AS SELECT * FROM `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;

-- select in non-partitioned table
-- 643 mb
SELECT DISTINCT(dispatching_base_num)
FROM `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_non_partitioned`
WHERE DATE(dropoff_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- select in partitioned table Q3Q4
-- 30.1mb
SELECT DISTINCT(dispatching_base_num)
FROM `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_Q3Q4`
WHERE DATE(dropoff_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- take a look at the partitioned table
SELECT table_name, partition_id, total_rows
FROM `trips_data_all.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'fhv_tripdata_2019_partitioned_Q3Q4'
ORDER BY total_rows DESC;


-- create partitioned and clustered table Q3Q4
CREATE OR REPLACE TABLE `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_clustered_Q3Q4`
PARTITION BY DATE(dropoff_datetime)
CLUSTER BY dispatching_base_num
AS SELECT * FROM `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;

-- select in partitioned table
-- 400.1MB
SELECT COUNT(*) AS trips
FROM `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_Q3Q4`
WHERE DATE(dropoff_datetime) BETWEEN '2019-01-01' AND '2019-03-31'
AND dispatching_base_num in ("B00987", "B02060", "B02279");

-- select in partitioned_clustered table
-- 400.1mb -> 133 mb
SELECT COUNT(*) AS trips
FROM `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_clustered_Q3Q4`
WHERE DATE(dropoff_datetime) BETWEEN '2019-01-01' AND '2019-03-31'
AND dispatching_base_num in ("B00987", "B02060", "B02279");



-- Q5

SELECT
  `dispatching_base_num`,
  COUNT(dispatching_base_num) AS counter
FROM
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`
GROUP BY
  dispatching_base_num
ORDER BY
  counter DESC;

--SR_Flag

SELECT
  `SR_Flag`,
  COUNT(SR_Flag) AS counter
FROM
  `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`
GROUP BY
  SR_Flag
ORDER BY
  counter DESC;

--- Create clustered and partitioned table for Q5
CREATE OR REPLACE TABLE `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_clustered_Q5`
CLUSTER BY dispatching_base_num,SR_Flag
AS SELECT * FROM `blissful-scout-339008.trips_data_all.external_fhv_tripdata_2019`;

-- select in unpartitioned table
-- 363 mb
SELECT COUNT(*) AS trips
FROM `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_non_partitioned`
WHERE SR_Flag=5
AND dispatching_base_num in ("B00987", "B02060", "B02279");

-- select in partitioned_clustered table
-- 9,9mb
SELECT COUNT(*) AS trips
FROM `blissful-scout-339008.trips_data_all.fhv_tripdata_2019_partitioned_clustered_Q5`
WHERE SR_Flag=5
AND dispatching_base_num in ("B00987", "B02060", "B02279");


-- Q6


-- Q7
-- Answer: proprietary columnar format called Capacitor