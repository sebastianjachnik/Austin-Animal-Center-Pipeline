# Austin Animal Center Pipeline

## Overview

This project builds an end-to-end data engineering pipeline based on the
**Austin Animal Center Intakes** and **Outcomes** datasets.

The goal is to ingest, store, transform, and analyze animal shelter data to generate meaningful insights.

---

## Datasets

* Austin Animal Center Intakes
* Austin Animal Center Outcomes

---

## Project Goals

* Build a reproducible data pipeline
* Load and store raw data
* Transform data into an analytical model
* Enable SQL-based analysis

---

## Planned Architecture

* Data ingestion (API / download)
* Storage (e.g. Google Cloud Storage)
* Data warehouse (BigQuery)
* Transformations (dbt)
* Orchestration (Kestra)

---

## Project Structure

```
Austin-Animal-Center-Pipeline/
├── ingestion/
├── orchestration/
├── terraform/
├── dbt/
├── sql/
├── data/
└── README.md
```

---

## Current Status

🚧 Project initialized

* Repository created
* Initial setup in progress
* Next step: data ingestion pipeline

---

## Next Steps

* Ingest both datasets
* Load into storage / warehouse
* Perform initial data exploration
* Build first transformations

---

## Tech Stack (planned)

* Python
* Google Cloud Platform (GCS, BigQuery)
* dbt
* Kestra
* Terraform
