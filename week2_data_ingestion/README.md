

# Airflow Dag

0. How to initialize Dag with Python
    - Context manager

1. Tasks
    1.1. Operators
    1.2. Sernsors
    1.3. Decorator

2. Task Dependency
    2.1 Set Upstream
    2.2 Set Downstream
    
    Q: How to do the branching? 
    Q: How to pass the data between tasks
        -> XCOM variable (push/pull metadata)
        -> Upload/Download large files

3. How to run DAG?
    DagRun is the


Pyarrow for converting to parquet files...
Revisit:  Advantages of Parquet 


4. GCP concepts: 
Google Cloud Storage Bucket vs BigQuery Dataaset
Understand GCP storage hierarchy, bucket, blob, etc..

5. Why Parquet better than the CSV in production level?
    - Compressed, faster
    - What else?