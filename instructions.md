# Project Setup Instructions

## 1. Clone the Repository
First, clone this repository to your local machine:
```sh
git clone https://github.com/sebastianjachnik/Austin-Animal-Center-Pipeline.git
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
Modify the following files with your project-specific values:
- `.env` (GCP configuration and credentials path)
- `terraform/variables.tf`

The `.env` file contains configuration such as:
- GCP project ID
- dataset and bucket names
- path to the service account credentials
- Kestra UI account credentials

These values are used by Kestra during pipeline execution.

Make sure the following variables in `terraform/variables.tf` are correctly set:
- `location`
- `bq_dataset_name`
- `gcs_bucket_name`


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

## 9. Provision Infrastructure (Terraform)
```sh
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

## 10. Run the Pipeline in Kestra
1. Open the Kestra UI: http://localhost:8080
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

## 11. Create the Dashboard in Looker Studio
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