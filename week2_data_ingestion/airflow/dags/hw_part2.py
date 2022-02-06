from datetime import datetime
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from workflow_utils.utils import prepare_filename, format_to_parquet, upload_to_gcs

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", 'blissful-scout-339008')
BUCKET = os.environ.get("GCP_GCS_BUCKET", 'dtc_data_lake_blissful-scout-339008')

PATH_TO_LOCAL_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

AWS_DATA_PREFIX = "https://nyc-tlc.s3.amazonaws.com/trip+data"
DATASET_PREFIX = "fhv_tripdata"


default_args = {
    "owner": "airflow",
    "start_date": datetime(2019, 1, 1),
    "end_date": datetime(2020, 12, 1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="hw_part2",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=['dtc-de'],
) as dag:

    prepare_filename = PythonOperator(task_id="prepare_filename",
                        python_callable=prepare_filename,
                        provide_context=True,
                        op_kwargs={
                            "logical_date": '{{ ds }}',
                            "dataset": DATASET_PREFIX
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
            dag = dag
        )

    cleanup = BashOperator(
        task_id="cleanup",
        bash_command=f'rm  {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_csv") }}}} {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="filename_parquet") }}}}'
    )

    prepare_filename >> download_dataset >> format_to_parquet >> upload_to_gcs >> cleanup
