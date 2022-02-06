from datetime import datetime
import os
import logging
from typing import Any, Dict

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq


PROJECT_ID = os.environ.get("GCP_PROJECT_ID", 'blissful-scout-339008')
BUCKET = os.environ.get("GCP_GCS_BUCKET", 'dtc_data_lake_blissful-scout-339008')
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')
PATH_TO_LOCAL_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

# #q3
# AWS_DATA_PREFIX = "https://nyc-tlc.s3.amazonaws.com/misc"
# DATASET_PREFIX = "taxi+_zone_lookup"
# q1q2
AWS_DATA_PREFIX = "https://nyc-tlc.s3.amazonaws.com/trip+data"
DATASET_PREFIX = "yellow_tripdata" #q1
DATASET_PREFIX = "fhv_tripdata" # q2


# TODO: Read specific yamls and store only yaml names here.
q1_config = {
    "default_args" : {
        "owner": "airflow",
        "start_date": datetime(2019, 1, 1),
        "end_date": datetime(2020, 12, 1),
        "depends_on_past": False,
        "retries": 1,},
    "schedule_interval": "@monthly",
    "AWS_DATA_PREFIX": "https://nyc-tlc.s3.amazonaws.com/trip+data",
    "DATASET_PREFIX": "yellow_tripdata",
    "BQ_ENABLED": True
}

q2_config = {
    "default_args" : {
        "owner": "airflow",
        "start_date": datetime(2019, 1, 1),
        "end_date": datetime(2020, 12, 1),
        "depends_on_past": False,
        "retries": 1,},
    "schedule_interval": "@monthly",
    "AWS_DATA_PREFIX": "https://nyc-tlc.s3.amazonaws.com/trip+data",
    "DATASET_PREFIX": "fhv_tripdata",
    "BQ_ENABLED": False
}

configs = [q1_config, q2_config]


def prepare_filename(logical_date:str,dataset:str, **kwargs):

    # TODO :try with Jinja    
    file_identifier = "-".join(logical_date.split('-')[:-1])
    filename_csv = f"{dataset}_{file_identifier}.csv"
    filename_parquet = filename_csv.replace('.csv', '.parquet')

    task_instance = kwargs['ti']
    task_instance.xcom_push(key="filename_csv", value=filename_csv)
    task_instance.xcom_push(key="filename_parquet", value=filename_parquet)
    logging.info("XCOM variables filename_csv and filename_parquet is successfully pushed..")


def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format!!")
        raise ValueError('Can only accept source files in CSV format!!')
    try:
        table = pv.read_csv(src_file)
        pq.write_table(table, src_file.replace('.csv', '.parquet'))
    except FileNotFoundError as e:
        logging.warning(f'FileNotFoundError: {src_file} does not exist')


def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


def generate_tasks(dataset:str, enable_bq:bool, **kwargs):

    prep = PythonOperator(
        task_id=f'prepare_filename_{dataset}',
        python_callable=prepare_filename,
        provide_context=True,
        op_kwargs={
            "logical_date": '{{ ds }}',
            "dataset": dataset
            },
    )

    download_file = BashOperator(
        task_id=f'download_dataset_{dataset}',
        bash_command=f'curl -sSLf {AWS_DATA_PREFIX}/{{{{ ti.xcom_pull(key="filename_csv") }}}} > {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}}'
    )

    format = PythonOperator(
        task_id=f'format_to_parquet_{dataset}',
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}}',
        },
    )

    upload = PythonOperator(
        task_id=f'upload_to_gcs_{dataset}',
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f'raw/{{{{ ti.xcom_pull(key="filename_parquet") }}}}',
            "local_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}',
        },
    )


    if enable_bq :
        bigquery_external_table = BigQueryCreateExternalTableOperator(
        task_id=f'bigquery_external_table_{dataset}',
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris":  [f'gs://{BUCKET}/raw/{{{{ti.xcom_pull(key="filename_parquet") }}}}'],
            },
        },
    )

    cleanup = BashOperator(
        task_id=f'cleanup_{dataset}',
        bash_command=f'rm  {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}} {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}'
    )

    if enable_bq:
        prep >> download_file >> format >> upload >> bigquery_external_table >> cleanup
    else:
        prep >> download_file >> format >> upload >> cleanup

    return prepare_filename, cleanup

def generate_dag(config:Dict[str, Any]):
    with DAG(
        dag_id="dag_{dataset}".format(dataset=config["DATASET_PREFIX"]),
        schedule_interval=config["schedule_interval"],
        default_args=config["default_args"],
        catchup=True,
        max_active_runs=3,
        tags=['dtc-de-hw'],
    ) as dag:
        generate_tasks(
            dataset=config["DATASET_PREFIX"],
            enable_bq= config["BQ_ENABLED"],
        )
    return dag
 
for config in configs:
    dataset = config['DATASET_PREFIX']
    globals()[f'dag_{dataset}'] = generate_dag(
        config = config
    )

