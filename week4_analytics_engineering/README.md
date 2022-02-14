
PS: The source code of week4- dbt project creadion can be found [here](https://github.com/IremErturk/dtc-dbt-taxi-rides-ny)

# Analytics Engineering
- Data Loading
- Data Storing (cloud data warehouses like Snowflake, BiqQuery, Redshift)
- *Data Modelling (tools like dbt, Dataform) (dont comfuse with ml models)
- *Data Presentation (BI tools like Google Data Studio, Looker, Mode or Tableu)

In otherwords, **analytics engineers** provide clean data sets to end users, modeling data in a way that empowers end users to answer their own questions. While a **data analyst** spends their time analyzing data, an **analytics engineer** spends their time transforming, testing, deploying, and documenting data. **Analytics engineers** apply software engineering best practices like version control and continuous integration to the analytics code base.

## Data Modelling
---
### 1 ETL vs ELT

### 2 Data warehouse Architecture Approaches

Concepts to keep in mind: normalized-denormalized data model
#### 2.1 Bill Inmon (top-down)
3NF, entity relationship model. 
Faster writes but queries are slow.

- Subject oriented
- Integrated
- Non-volatile

#### 2.2 Kimballs' Dimentional Modelling (bottom-up[])
Objective: Deliver data understandable to the business users, deliver fast query performance
Approach: Priotrize user understandability and query performance over non redundant data(3NF)

**Star Schema / Elements of Dimentional Modelling**
Particular way of organizing data for analytical purpose. It consists of two types of tables.
- Facts Tables: acts as primary table for the schema
    -  measurements metrics or facts
    -  corresponds to business process
    -  "verbs"
- Dimentional Tables:
    - provide context to a business
    - corresponds to business entity
    - "nouns"

#### 2.3 Data Vault

More agile way of modeling the datawarehouse. It can be seen as hybrid approach that combines
Bill Innons 3NF relation-entity model and Kimbals Dimentional model.

In 3NF: each table should have unique identifier for its elements by  PK+datetimestamp
Whenever change needed in parent table, the cascading effect on concequent child tables.

In Star Schema: The fact table aggregated table with information in dimentional tables through FK


Data Vault has three main components:
- Hub: Business Key, for instance employee id
- Satellite: Descriptors of the Hubs (where all history stored, ...)
- Link: Unique link between two hubs are reprsents the relationship

## DBT
---
is an transformation tool that allows anyone that knows SQL to deploy analytics code 
following software engineering best practices like modularity, portability, CI/CD and documentation


## References and Further Reads
---
- [What is analytics engineering?](https://www.getdbt.com/what-is-analytics-engineering/)
- **[dbt and the Analytics Engineer — what’s the hype about](https://medium.com/validio/dbt-and-the-analytics-engineer-whats-the-hype-about-907eb86c4938)
- **[DBT vs Apache Spark](https://medium.com/datamindedbe/why-dbt-will-one-day-be-bigger-than-spark-2225cadbdad0)
- [Kimbals Dimensional Data Modelling](https://www.holistics.io/books/setup-analytics/kimball-s-dimensional-data-modeling/)
- **[Data Vault](https://www.youtube.com/watch?v=l5UcUEt1IzM)
