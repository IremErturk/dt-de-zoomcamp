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


config = {
    "default_args" : {
        "owner": "airflow",
        "start_date": datetime(2019, 1, 1),
        "end_date": datetime(2020, 12, 1),
        "depends_on_past": False,
        "retries": 1,},
    "schedule_interval": "@monthly",
    "dag_id": "dag_green_tripdata",
    "data_base_url": "https://nyc-tlc.s3.amazonaws.com/trip+data",
    "dataset": "green_tripdata",
    "bq_enabled": False

}

def prepare_filename(logical_date:str, dataset:str, schedule_interval:str, **kwargs):

    if schedule_interval == "@once":
        filename_csv = f"{dataset}.csv"
    else:
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


def generate_tasks(base_url:str, dataset:str, schedule_interval:str, enable_bq:bool, **kwargs):

    prep = PythonOperator(
        task_id=f'prepare_filename',
        python_callable=prepare_filename,
        provide_context=True,
        op_kwargs={
            "logical_date": '{{ ds }}',
            "dataset": dataset,
            "schedule_interval": schedule_interval
            },
    )

    download_file = BashOperator(
        task_id=f'download_dataset',
        bash_command=f'curl -sSLf {base_url}/{{{{ ti.xcom_pull(key="filename_csv") }}}} > {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}}'
    )

    format = PythonOperator(
        task_id=f'format_to_parquet',
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}}',
        },
    )

    upload = PythonOperator(
        task_id=f'upload_to_gcs',
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f'raw/{{{{ ti.xcom_pull(key="filename_parquet") }}}}',
            "local_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}',
        },
    )


    if enable_bq :
        bigquery_external_table = BigQueryCreateExternalTableOperator(
        task_id=f'bigquery_external_table',
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
        task_id=f'cleanup',
        bash_command=f'rm  {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}} {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}'
    )

    if enable_bq:
        prep >> download_file >> format >> upload >> bigquery_external_table >> cleanup
    else:
        prep >> download_file >> format >> upload >> cleanup

    return prepare_filename, cleanup

def generate_dag(config:Dict[str, Any]):
    with DAG(
        dag_id= config["dag_id"],
        schedule_interval=config["schedule_interval"],
        default_args=config["default_args"],
        catchup=True,
        max_active_runs=3,
        tags=['dtc-de-hw'],
    ) as dag:
        generate_tasks(
            base_url = config["data_base_url"],
            dataset=config["dataset"],
            schedule_interval= config["schedule_interval"],
            enable_bq= config["bq_enabled"],
        )
    return dag
 

globals()[f'dag_green_tripdata'] = generate_dag(config = config)

