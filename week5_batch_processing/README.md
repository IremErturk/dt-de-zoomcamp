## Apache Spark

### Spark Cluster and Repartitioning files

In Spark Cluster, there are number of processors and each processor process one file at a time.
If we have one big file, then the file can be handled by only one processor and the rest of processors stay in idle state.

To equally distribute the processing power, the best practice to have more data files than the processors exists.
Repartiotion of single big file comes handy after that point :) 