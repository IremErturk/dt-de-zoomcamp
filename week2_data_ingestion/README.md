# Airflow

One thing to wrap your head around is that this Airflow Python script is really just a configuration file specifying the DAG’s structure as code. The actual tasks defined here will run in a different context from the context of this script. Different tasks run on different workers at different points in time, which means that this script cannot be used to cross communicate between tasks. Note that for this purpose we have a more advanced feature called [XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html).

## Core Ideas 
### DAG
A DAG is defined in a Python script, which represents the DAGs structure (tasks and their dependencies) as code. The important thing is that the DAG isn't concerned with what its constituent tasks do; its job is to make sure that whatever they do happens at the right time, or in the right order, or with the right handling of any unexpected issues.

**How Airflow finds Dags ?**: When searching for DAGs, Airflow only considers Python files that contain the strings "airflow" and "dag" by default (case-insensitive). To consider all Python files instead, disable the DAG_DISCOVERY_SAFE_MODE configuration flag.

#### Dag Runs & Catchup

##### Catchup
In Airflow DAG with a `start_date`, possibly an `end_date`, and a `schedule_interval` defines a series of intervals which the scheduler turns into individual DAG Runs and executes. The scheduler, by default, will kick off a DAG Run for any interval that has not been run since the last execution date (or has been cleared). This concept is called Catchup, please check [here](https://airflow.apache.org/docs/apache-airflow/2.0.0/dag-run.html#catchup) for details.

If your DAG is written to handle its catchup (i.e., not limited to the interval, but instead to Now for instance.), then you will want to turn catchup off. This can be done by setting `catchup = False` in DAG or `catchup_by_default = False` in the configuration file. When turned off, the scheduler creates a DAG run only for the latest interval.

Note: In the homework, we need to set `catchup=True` as we are interested to run the data ingestion pipeline for specific time range.


#### Creating Dags
1. Context Manager
2. Dag Decorator: Any function decorated with `@dag` returns a DAG object. This allows you to parametrize your DAGs and set the parameters when triggering the DAG manually. You can also use the parameters on jinja templates.
#### TaskFlow API / Functional Dags
Outputs and inputs are sent between tasks using XCOM values


### Tasks
Task decorator `@dag.task` captures returned values and sends them to the XCom backend. By default, the returned value is saved as a single XCom value. You can set multiple_outputs key argument to True to unroll dictionaries, lists or tuples into separate XCom values. This can be used with regular operators to create DAGs with Task Flow API.

Calling a decorated function returns an XComArg instance. You can use it to set templated fields on downstream operators.

To retrieve current execution context you can use `get_current_context` method. In this way you can gain access to context dictionary from within your operators. This is especially helpful when using `@task` decorator. Current context is accessible only during the task execution. The context is not accessible during pre_execute or post_execute. Calling this method outside execution context will raise an error.

We recommend you setting operator relationships with bitshift operators rather than set_upstream() and set_downstream().
### Operators
While DAGs describe how to run a workflow, Operators determine what actually gets done by a task.


**Good Set of Resource to understand the Airflow Data Interval Concept**
- [Airflow Tips and Best Practices](https://towardsdatascience.com/apache-airflow-tips-and-best-practices-ff64ce92ef8#:~:text=The%20execution%20time%20in%20Airflow,on%202019%E2%80%9312%E2%80%9306.)
- [Airflow Schedule Interval 101](https://towardsdatascience.com/airflow-schedule-interval-101-bbdda31cc463)
- [How to use Variables and XCom in Apache Airflow](https://maciejszymczyk.medium.com/how-to-use-variables-and-xcom-in-apache-airflow-5eb313adbde1)
- [XCom Example](https://github.com/apache/airflow/blob/main/airflow/example_dags/example_xcom.py)
- [Official Airflow Document for Templates reference](https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html)
- [Official Airflow FAQ](https://airflow.apache.org/docs/apache-airflow/stable/faq.html#faq)
- [Official Airflow Document for Concepts](https://airflow.apache.org/docs/apache-airflow/2.0.0/concepts.html#execution-date)
- [Official Airflow Pipline Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)


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
    4.1 Google Cloud Storage Bucket vs BigQuery Dataaset
    4.2 Understand GCP storage hierarchy, bucket, blob, etc..
    4.3 Transfer Service

5. Why Parquet better than the CSV in production level?
    - Compressed, faster
    - What else?


6. OLAP(Online Analytical Processing) vs OLTP(Online Transactional Processing)

- OLTP 
-   in backend services, to run sql queries and rollback/fallback incase one fails
-   updates are short, fast updates iniciated by user
-   
- OLAP lots of data in and finding hidden insights
-   data is periodically refreshed
-   denormalized data


Datawarehouse (Olap solution)
- Raw / Metadata/ Summary

BiqQuery 
- Datawarehouse solution  + Serverless
- Flexibity by seperating the compute engine that analyzes your data from your source
