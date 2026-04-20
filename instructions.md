# Project Setup Instructions

## 1. Clone the Repository
First, clone this repository to your local machine:
```sh
git clone <YOUR_REPO_URL>
```
Then, navigate into the project folder:
```sh
cd Austin-Animal-Center-Pipeline
```

## 2. Create a Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project.

## 3. Create a Service Account
1. Navigate to IAM & Admin > Service Accounts.
2. Click Create Service Account.
3. Assign the following roles:
   - Storage Admin (for GCS access)
   - BigQuery Admin (for BigQuery access)
4. Click Done.

## 4. Generate a JSON Key
1. In the Service Accounts section, find your newly created service account.
2. Click on it and go to the Keys tab.
3. Click Add Key > Create new key.
4. Select JSON and download the key.
5. Move the JSON key to:
   `terraform/keys/my-creds.json`

## 5. Update Configuration Files
Modify the following file with your project-specific values:
- `.env`
- `terraform/variables.tf`


Make sure the following variables are correctly set:
- `project`
- `region`
- `gcs_bucket_name`
- `bq_dataset_name`

## 6. Install Dependencies
Install dependencies using uv:
```sh
uv sync
```

## 7. Start Kestra
Run:
```sh
docker compose up -d
```

Wait until Kestra is fully running.

## 8. Deploy Kestra Flows
```sh
uv run python kestra/deploy_kestra.py
```

### Note on dbt Sync

Ensure that the `03_gcp_dbt` workflow is configured with the correct repository URL:

```yaml
tasks:
  - id: sync
    type: io.kestra.plugin.git.SyncNamespaceFiles
    url: https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>
    branch: main
    namespace: "{{flow.namespace}}"
    gitDirectory: dbt/austin_animal_center
    dryRun: false
```

This step ensures that Kestra can fetch the dbt project from your repository.

## 9. Provision Infrastructure (Terraform)
```sh
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

## 10. Configure Kestra KV Store
In the Kestra UI, configure the following key-value pairs:

- `GCP_PROJECT_ID`
- `GCP_DATASET`
- `GCP_BUCKET_NAME`
- `GCP_LOCATION`
- `GCP_CREDS`

## 11. Run the Pipeline in Kestra
1. Open Kestra-UI: http://localhost:8080
2. Navigate to:
   `04_master_pipeline`
3. Execute the flow.

This pipeline will:
- Ingest intake and outcome data
- Upload data to Google Cloud Storage
- Load data into BigQuery (partitioned and clustered tables)
- Run dbt transformations:
  - staging: cleaning
  - intermediate: joining datasets
  - marts: computing stay duration

## 12. Create the Dashboard in Looker Studio
1. Connect Looker Studio to BigQuery.
2. Use the table:
   `fct_animal_stays`
3. Build visualizations:
   - Average stay duration over time
   - Distribution of outcome types

---

Now you're ready to analyze animal shelter data with Looker Studio 🚀

Optional cleanup:
```sh
terraform destroy
```