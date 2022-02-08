# OLAP vs OLTP

|                       | OLTP (Online Transactional Processing)                         | OLAP (Online Analytical Processing)   |
| :---                  | :----                                                          |  :---   |
| Purpose               | Control and run essential business operartions in real time    | Plan solve problems , support decisions, discover hidden insights|
| Data Updates          | Short fast updates, initiated by used                          | Periodically refreshed data with scheduled, log running batch jobs|
| Database Design       | Normalized database for effieciency                            | Denormalized data for analysis  |
| Space Requirements    | Small if historical data is archieved                          | Large due to aggregating data sets |
| Backup and Recovery   | Regular backups, meet legal and governance requirements        | Lost data can be reloaded, as regular backups neede |
| Productivity          | Increase productivity of end user                              | Increase productivity of business manager, data analyst, and executives |
| Data View             | List day-to day business transactions                          | Multi dimentional view of enterprise data  |
| Use-Cases             | Customer facing personnel, clerks, online shoppers             | Knowledge workers such as data analyst, business analyst and executives |


# Datawarehouse (OLAP solution)
- Used for reporting and data analysis
- Raw / Metadata/ Summary

## BiqQuery (BQ)
- Datawarehouse solution  + Serverless(**)
- Flexibity by seperating the compute engine that analyzes your data from your source
- Concepts : Project -> Dataset -> Tables

### Partitioning vs Clustering

|Clustering                                                                            | Partitioning   |
| :----                                                                                |  :---   |
| Cost benefit unknown                                                                 | Cost known upfront|
| Need more granularity than partitioning                                              | Partition level management needed |
| Your queries commonly use filter or aggregation against multiple particular columns  | Filter or aggreagate on single column  |
| The cardinality of the number of values in a column or group of columns is large     | --- Limitation as allows only 4000 partitions |
| Regular backups, meet legal and governance requirements                              | Lost data can be reloaded, as regular backups neede |
| Increase productivity of end user                                                    | Increase productivity of business manager, data analyst, and executives |
| List day-to day business transactions                                                | Multi dimentional view of enterprise data  |
| Customer facing personnel, clerks, online shoppers                                   | Knowledge workers such as data analyst, business analyst and executives |
#### Partitioning 
- Partitioning the table for performance improvement on queries
- partition_id and total_rows 
- Partitions can be querable as well (different than querying tables) -> to check the balance between the partition groups
- Caution: Number of partition is limited to 4000, therefore consider while partitioning by hourly for instance.
- Only one partitioning column is allowed, and it has to be either TIMESTAMP/DATE or INTEGER
- When using Time unit or ingestion time , daily is the default, hourly, monthly and yearly options available

#### Clustering
- Clustering , query performance + cost improvement
- Caution: The order of clustering columns is important (upto 4 clustering columns)
- Improves filter and aggreate queries (specially on the clustered columns)

#### Automatic Reclustering
1. As data added to the clustered table
    The newly inserted data can be written to blocks that contain key ranges that overlap with the key ranges in previous written blocks
    The overlapping keys weaken the sort propertu of the table
2. To maintain performance charecteristics of clustered table
    run in the backgroun to restore sort property of the table
    for partitioned tables, clustering is maintained for data within the scope of each partition.

### Best Practices
1. Cost Reduction
    - Avoid SELECT *, (whenever only specific column)
    - Price your queries before running
    - Use clustered or partitioned tables
    - Use streaming inserts with caution
    - Materialize query results in stages







### Machine Learning