# Week1: Learnings & Helpful Resources

## Docker
- `docker build`: create Docker image based on the Dockerfile
- `docker run`: create Docker container for the Docker image

1. Dockerfile


2. [CMD](https://docs.docker.com/engine/reference/builder/#cmd) vs [ENTRYPOINT](https://docs.docker.com/engine/reference/builder/#entrypoint)
    - [EntryPoints 5 Use-cases](https://medium.com/swlh/five-use-cases-for-docker-entry-points-a5eb6661dac6)
    - [Run vs CMD vs Entrypoint](https://goinbigdata.com/docker-run-vs-cmd-vs-entrypoint/)

3. Workdir vs  Run Cd
    - `run cd` doesn’t change the directory in global level but only on the current command line. Check stackoverflow discussion regarding that [here](https://stackoverflow.com/questions/58847410/difference-between-run-cd-and-workdir-in-dockerfile).
    - What is WORKDIR? (Any RUN, CMD, ADD, COPY or ENTRYPOINT) <!-- - TODO: -->

4. COPY

5. How to connect multiple Docker Containers?
    - For instance how PgAdmin container will communicate with the Postgres container? (arent they isolated?)
    - With Docker Network or With Docker Compose
    - Docker Compose, the common network for the services/containers are created automatically. It is useful as we can put multiple service configuration in one single yaml file. Otherwise, the common network should be created before creating the docker containers. In each `docker run` --network and --name should be defined. 

5. Docker Container Exit Codes
    - Which are the valid exit codes for Docker? <!-- TODO --> 
    - What happens in case of invalid exit code  <!-- TODO: --> 


## SQL

1. Querying on more than one table
    - JOIN
2. Transactions <!-- TODO -->
3. Postgres clients: sqlalchemy vs psycopg2
    - What is SQLAlchemy? : An ORM is a database abstraction layer that sits as an intermediary between you and the database engine. It allows you to define regular Python objects and methods and translates them into low-level SQL database instructions for you.
    - [Here is the reason why SQLAlchemy is so popular](https://towardsdatascience.com/here-is-the-reason-why-sqlalchemy-is-so-popular-43b489d3fb00)
    - [Differences in syntax](https://pplonski.github.io/sqlalchemy-vs-psycopg2/)


## GCP

1. Service Account vs User Account
    - Service accounts are managed by IAM.They are intended for scenarios where your application needs to access resources or perform actions on its own. Such as IAM roles in AWS
    - [Authenticating as service account](https://cloud.google.com/docs/authentication/production)

2. Roles and Service Accounts
    - It is generally better idea to create multiple service account for each service, and assign only required roles to these service accounts. For instance, as terraform should be able to create, destroy and update resources, we should give all admin roles to terraform service, where as data pipeline only need write access to database and read access to the datalake.     <!-- TODO -->
    - Storage Admin vs Storage Object Admin ? Storage Admin defined on the bucket level where as Storage Object Admin role defined in the object level in the bucket.
 

## IaC and Terraform

1. How to manage multiple terraform versions for each project: tfenv, tfswitch.
    - [Manage multiple Terraform versions with tfenv](https://opensource.com/article/20/11/tfenv)
    - [How to manage different terraform versions for each project](https://warrensbox.medium.com/how-to-manage-different-terraform-versions-for-each-project-51cca80ccece#:~:text=You%20can%20switch%20between%20different,the%20up%20and%20down%20arrow.)
    - .terraform-version vs ..

2. Best Practices for Terraform
    - [Best Practices](https://www.terraform-best-practices.com/)
    - [10 TERRAFORM BEST PRACTICES](https://openupthecloud.com/terraform-best-practices/)
    - [Terraform Best Practices](https://medium.com/codex/terraform-best-practices-testing-your-code-f25053b06c4c)
    - backend (how and where to store the terraform state file)
    - modularize as much as possible to increase the reusablity and maintability of the IaC
    - How to define same providers, and associate with the resources? For instance in our example, there is one google provider and all resources are associated with the provider, therefore we dont need to specify provider value in resource blocks. However, if we have multiple google providers, we need to distinguish them by using alias within the provider blocks and whenver google provider related resource block written which provider should be defined.
    5. locals

3. Terragrunt vs Terraform vs Terraspace
    - Terragrunt is a thin Terraform wrapper that provides tooling and some opinions. Instead of calling terraform directly, you call terragrunt commands, which, in turn, call the corresponding terraform commands 
    - [Terraform vs Terragrunt vs Terraspace](https://blog.boltops.com/2020/09/28/terraform-vs-terragrunt-vs-terraspace/)  <!-- TODO -->


## More Topics

1. SFTP  <!-- TODO -->