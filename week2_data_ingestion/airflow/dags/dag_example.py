from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def print_hello():
        print("Hello world!")

default_args = {
        'owner': 'irem.ertuerk',
        'start_date': datetime(2019, 1, 1),
}

dag = DAG('dag-example', 
        description='Simple Dag Example',
        schedule_interval="@yearly",
        default_args = default_args, 
        catchup=True)

dummy_operator = DummyOperator(task_id='dummy_task', retries=3, dag=dag)

hello_operator = PythonOperator(task_id='hello_task', python_callable=print_hello, dag=dag)

dummy_operator >> hello_operator