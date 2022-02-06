# Airflow

One thing to wrap your head around is that this Airflow Python script is really just a configuration file specifying the DAG’s structure as code. The actual tasks defined here will run in a different context from the context of this script. Different tasks run on different workers at different points in time, which means that this script cannot be used to cross communicate between tasks. Note that for this purpose we have a more advanced feature called [XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html).

## Core Ideas 
### DAG
A DAG is defined in a Python script, which represents the DAGs structure (tasks and their dependencies) as code. The important thing is that the DAG isn't concerned with what its constituent tasks do; its job is to make sure that whatever they do happens at the right time, or in the right order, or with the right handling of any unexpected issues.

**How Airflow finds Dags ?**: When searching for DAGs, Airflow only considers Python files that contain the strings "airflow" and "dag" by default (case-insensitive). To consider all Python files instead, disable the DAG_DISCOVERY_SAFE_MODE configuration flag.

#### Dag Runs & Catchup

In below, I am documenting the description of attributes and behaviours.
To get a detailed overview with example that focus how DAG Runs are scheduled and how catchup, start_date, schedule_interval effects the behaviour,  please check my medium article (here (coming soon))

##### execution_date

The execution_date is the logical date and time which the DAG Run, and its task instances, are running for.

This allows task instances to process data for the desired logical date & time. While a task_instance or DAG run might have an actual start date of now, their logical date might be 3 months ago because we are busy reloading something.

A DAG run and all task instances created within it are instanced with the same execution_date, so that logically you can think of a DAG run as simulating the DAG running all of its tasks at some previous date & time specified by the execution_date.

##### Catchup
In Airflow DAG with a `start_date`, possibly an `end_date`, and a `schedule_interval` defines a series of intervals which the scheduler turns into individual DAG Runs and executes. The scheduler, by default, will kick off a DAG Run for any interval that has not been run since the last execution date (or has been cleared). This concept is called Catchup, please check [here](https://airflow.apache.org/docs/apache-airflow/2.0.0/dag-run.html#catchup) for details.

If your DAG is written to handle its catchup (i.e., not limited to the interval, but instead to Now for instance.), then you will want to turn catchup off. This can be done by setting `catchup = False` in DAG or `catchup_by_default = False` in the configuration file. When turned off, the scheduler creates a DAG run only for the latest interval.

Note: In the homework, we need to set `catchup=True` as we are interested to run the data ingestion pipeline for specific time range.


#### Creating Dags
1. Context Manager
2. Dag Decorator: Any function decorated with `@dag` returns a DAG object. This allows you to parametrize your DAGs and set the parameters when triggering the DAG manually. You can also use the parameters on jinja templates.

# Factory Approach for DAG creation:
To reduce code dublication and logical similarity between three dag files, I have worked on implementing dag factory approach.
However, from Airflow Webserver, I have received `raise AirflowTaskTimeout(self.error_message)set` error which refers that creating multiple
dags from a single dag file cause performance issues. Please check the details from [here](https://airflow.apache.org/docs/apache-airflow/2.2.3/best-practices.html#reducing-dag-complexity)


### Tasks
Task decorator `@dag.task` captures returned values and sends them to the XCom backend. By default, the returned value is saved as a single XCom value. You can set multiple_outputs key argument to True to unroll dictionaries, lists or tuples into separate XCom values. This can be used with regular operators to create DAGs with Task Flow API.

Calling a decorated function returns an XComArg instance. You can use it to set templated fields on downstream operators.

To retrieve current execution context you can use `get_current_context` method. In this way you can gain access to context dictionary from within your operators. This is especially helpful when using `@task` decorator. Current context is accessible only during the task execution. The context is not accessible during pre_execute or post_execute. Calling this method outside execution context will raise an error.

We recommend you setting operator relationships with bitshift operators rather than set_upstream() and set_downstream().

### Operators
While DAGs describe how to run a workflow, Operators determine what actually gets done by a task.

### Further Resources

**Best Practices**
- [DAG Writing Best Practices in Apache Airflow](https://www.astronomer.io/guides/dag-best-practices)

**Scheduler and DagRuns**
- [Airflow Tips and Best Practices](https://towardsdatascience.com/apache-airflow-tips-and-best-practices-ff64ce92ef8#:~:text=The%20execution%20time%20in%20Airflow,on%202019%E2%80%9312%E2%80%9306.)
- [Airflow Schedule Interval 101](https://towardsdatascience.com/airflow-schedule-interval-101-bbdda31cc463)

**XCom and Variables**
- [How to use Variables and XCom in Apache Airflow](https://maciejszymczyk.medium.com/how-to-use-variables-and-xcom-in-apache-airflow-5eb313adbde1)
- [XCom Example](https://github.com/apache/airflow/blob/main/airflow/example_dags/example_xcom.py)

**Branching**
- [Branch Operator](https://www.astronomer.io/guides/airflow-branch-operator)
- [Branching Example](https://stackoverflow.com/questions/67427144/how-to-branch-multiple-paths-in-airflow-dag-using-branch-operator)

**Testing** #TODO
- [Testing Airflow](https://www.astronomer.io/guides/testing-airflow)
- [Data’s Inferno: 7 Circles of Data Testing Hell with Airflow](https://medium.com/wbaa/datas-inferno-7-circles-of-data-testing-hell-with-airflow-cef4adff58d8)
- [Testing in Airflow Part 1 — DAG Validation Tests, DAG Definition Tests and Unit Tests](https://medium.com/@chandukavar/testing-in-airflow-part-1-dag-validation-tests-dag-definition-tests-and-unit-tests-2aa94970570c)

**Important References from Offical Document**
- [Official Airflow Document for Module Management](https://airflow.apache.org/docs/apache-airflow/stable/modules_management.html)
- [Official Airflow Document for Concepts](https://airflow.apache.org/docs/apache-airflow/2.0.0/concepts.html#execution-date)
- [Official Airflow Pipeline Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
- [Official Airflow Document for Templates reference](https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html)
- [Official Airflow FAQ](https://airflow.apache.org/docs/apache-airflow/stable/faq.html#faq)



4. GCP concepts: 
    4.1 Google Cloud Storage Bucket vs BigQuery Dataaset
    4.2 Understand GCP storage hierarchy, bucket, blob, etc..
    4.3 Transfer Service

5. Why Parquet better than the CSV in production level?
    - Compressed, faster
    - What else?
