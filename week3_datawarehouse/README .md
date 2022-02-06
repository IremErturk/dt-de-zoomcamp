OLAP(Online Analytical Processing) vs OLTP(Online Transactional Processing)

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