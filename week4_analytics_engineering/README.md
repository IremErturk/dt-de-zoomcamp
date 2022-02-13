
PS: The source code of week4- dbt project creadion can be found [here](https://github.com/IremErturk/dtc-dbt-taxi-rides-ny)

# Analytics Engineering
- Data Loading
- Data Storing (cloud data warehouses like Snowflake, BiqQuery, Redshift)
- *Data Modelling (tools like dbt, Dataform)
- *Data Presentation (BI tools like Google Data Studio, Looker, Mode or Tableu)

## Data Modelling

### ETL vs ELT


### Approaches

#### Kimballs' Dimentional Modelling / Star Schema
Objective: Deliver data understandable to the business users, deliver fast query performance
Approach: Priotrize user understandability and query performance over non redundant data(3NF)

**Elements of Dimentional Modelling** 
- Facts Tables: 
    -  measurements metrics or facts
    -  corresponds to business process
    -  "verbs"
- Dimentional Tables:
    - provide context to a business
    - corresponds to business entity
    - "nouns"

<!-- TODO -->
### Bill Inmon 
### Data Vault

### DBT
is an transformation tool that allows anyone that knows SQL to deploy analytics code 
following software engineering best practices like modularity, portability, CI/CD and documentation

<!-- TODO: Spart vs DBT -->

**dbt-Core**
**dbt-Cloud**