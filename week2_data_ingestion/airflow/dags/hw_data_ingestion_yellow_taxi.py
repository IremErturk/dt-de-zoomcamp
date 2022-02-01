import imp
import os
import logging
from typing import List

import pandas as pd

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", 'blissful-scout-339008')
BUCKET = os.environ.get("GCP_GCS_BUCKET", 'dtc_data_lake_blissful-scout-339008')
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

DATASET_PREFIX = "yellow_tripdata"
START_YEAR, END_YEAR    = "2019-01", "2020-12"

def find_dataset_filenames(dataset_prefix:str=DATASET_PREFIX, start_year:str=START_YEAR, end_year:str=END_YEAR ) -> List[str]:
    dataset_files = [f"{dataset_prefix}_{dm}.csv" for dm in pd.date_range(start_year, end_year, freq='MS').strftime("%Y-%m").tolist()]
    return dataset_files

FILES = find_dataset_filenames()
FILES_BASH = " ".join(FILES)


AWS_DATA_PREFIX = "https://nyc-tlc.s3.amazonaws.com/trip+data"

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")



def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    try:
        table = pv.read_csv(src_file)
        pq.write_table(table, src_file.replace('.csv', '.parquet'))
    except FileNotFoundError as e:
        logging.warning(f'FileNotFoundError: {src_file} does not exist')

def format_files_to_parquet():
    for file in FILES:
        format_to_parquet(f"{path_to_local_home}/{file}")

def upload_files_to_gcs(bucket:str):

    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    for file in FILES:
        logging.info(f"File {file} is start uploding to GCP")
        parquet_filename = file.replace('.csv', '.parquet')
        gcp_object_name = f"raw/{parquet_filename}"
        local_filepath = f"{path_to_local_home}/{parquet_filename}"
        blob = bucket.blob(gcp_object_name)
        try:
            blob.upload_from_filename(local_filepath)
        except FileNotFoundError as e:
            logging.warning(f'{e.strerror}: {local_filepath} does not exist')


def find_all_parquet_file_urls(bucket:str):
    client = storage.Client()
    blob_uris = []
    for blob in client.list_blobs(bucket, prefix='raw/'):
        blob_uri = f"gs://{BUCKET}/{blob.name}"
        blob_uris.append(blob_uri)
        
    return blob_uris


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1), # TODO: HW not sure what changes based on that...,
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="hw_data_ingestion_yellow_taxi",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    download_dataset = BashOperator(
        task_id="download_dataset",
        bash_command= f""" for i in {FILES_BASH}
                            do
                                curl -sSLf {AWS_DATA_PREFIX}/$i > {path_to_local_home}/$i
                                echo "{AWS_DATA_PREFIX}/$i"
                            done
                        """
    )

    format_files_to_parquet = PythonOperator(
        task_id="format_files_to_parquet",
        python_callable=format_files_to_parquet,
    )

    upload_files_to_gcs = PythonOperator(
        task_id="upload_files_to_gcs",
        python_callable=upload_files_to_gcs,
        op_kwargs={
            "bucket": BUCKET
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
                "sourceUris": find_all_parquet_file_urls(bucket=BUCKET)
            },
        },
    )

    download_dataset >> format_files_to_parquet >> upload_files_to_gcs >> bigquery_external_table
