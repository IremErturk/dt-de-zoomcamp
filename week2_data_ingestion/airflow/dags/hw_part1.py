from datetime import datetime
import os
import logging

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

AWS_DATA_PREFIX = "https://nyc-tlc.s3.amazonaws.com/trip+data"
DATASET_PREFIX = "yellow_tripdata"


def prepare_filename(logical_date:str,dataset:str=DATASET_PREFIX, **kwargs):
    
    file_identifier = "-".join(logical_date.split('-')[:-1])
    filename_csv = f"{dataset}_{file_identifier}.csv"
    filename_parquet = filename_csv.replace('.csv', '.parquet')

    task_instance = kwargs['ti']
    task_instance.xcom_push(key="filename_csv", value=filename_csv)
    task_instance.xcom_push(key="filename_parquet", value=filename_parquet)
    logging.info("XCOM variables filename_csv and filename_parquet is successfully pushed..")


def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
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


default_args = {
    "owner": "airflow",
    "start_date": datetime(2019, 1, 1),
    "end_date": datetime(2020, 12, 1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="v5_hw_data_ingestion_yellow_taxi",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=['dtc-de'],
) as dag:

    prepare_filename = PythonOperator(
        task_id="prepare_filename",
        python_callable=prepare_filename,
        provide_context=True,
        op_kwargs={
            "logical_date": '{{ ds }}'
            },
    )
    
    download_dataset = BashOperator(
        task_id="download_dataset",
        bash_command=f'curl -sSLf {AWS_DATA_PREFIX}/{{{{ ti.xcom_pull(key="filename_csv") }}}} > {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}}'
    )

    format_to_parquet= PythonOperator(
        task_id="format_to_parquet",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}}',
        },
    )

    upload_to_gcs = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f'raw/{{{{ ti.xcom_pull(key="filename_parquet") }}}}',
            "local_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}',
        },
    )

    bigquery_external_table = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table",
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
        task_id="download_dataset",
        bash_command=f'rm  {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}} {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}'
    )

    
    prepare_filename >> download_dataset >> format_to_parquet >> upload_to_gcs >> bigquery_external_table >> cleanup
