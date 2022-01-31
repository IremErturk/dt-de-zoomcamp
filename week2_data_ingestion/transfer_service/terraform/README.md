### Concepts
* [Terraform_overview](../1_terraform_overview.md)
* [Audio](https://drive.google.com/file/d/1IqMRDwJV-m0v9_le_i2HA_UbM_sIWgWx/view?usp=sharing)


### Generate AWS Access key (for being able to use transfer-service)
- Login in to AWS account  
- Search for IAM
  ![aws iam](../../images/aws/iam.png)
- Click on `Manage access key`
- Click on `Create New Access Key`
- Download the csv, your access key and secret would be in that csv (Please note that once lost secret cannot be recovered)

## Transfer service
https://console.cloud.google.com/transfer/cloud/jobs

### Execution

```shell
# Refresh service-account's auth-token for this session
gcloud auth application-default login

# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan -var="project=<your-project-id>"
```

```shell
# Create new infra
terraform apply -var="project=<your-project-id>"
```

```shell
# Delete infra after your work, to avoid costs on any running services
terraform destroy
```
