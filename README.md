# Austin Animal Center Data Pipeline

This is my submission for the [Data Engineering Zoomcamp 2026](https://github.com/DataTalksClub/data-engineering-zoomcamp) final project.

## Problem Description

The Austin Animal Center dataset contains information about animals entering and leaving an animal shelter.

The goal of this project is to build an end-to-end data pipeline to analyze animal stay patterns and answer the following questions:

- How has the average stay duration of animals changed over time?
- How are different outcome types distributed (e.g., adoption, transfer, euthanasia)?

This analysis provides insights into shelter efficiency and animal lifecycle trends.

## Data

The dataset is sourced from the Austin Animal Center public data.

It consists of two main tables:

- Intakes – information about animals entering the shelter
- Outcomes – information about animals leaving the shelter

Source links:
- [Austin Animal Center Intakes](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data)
- [Austin Animal Center Outcomes](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data)

These datasets are combined to compute animal stay duration.

## Technologies Used

- Docker – containerized environment
- Python – data ingestion scripts
- Terraform – infrastructure as code
- Kestra – workflow orchestration
- Google Cloud Storage (GCS) – data lake
- BigQuery – data warehouse
- dbt – data transformation (staging → intermediate → marts)
- Looker Studio – dashboard visualization

## Data Pipeline

The pipeline processes data in batch mode and is orchestrated using Kestra.
It consists of the following steps:

1. Ingestion  
   Data is fetched via API and stored as parquet files in GCS  

2. Data Loading  
   Raw data is loaded into BigQuery as partitioned and clustered tables  

3. Transformation (dbt)  
   - staging: clean and standardize data  
   - intermediate: join intakes and outcomes  
   - marts: compute stay duration (`fct_animal_stays`)  

4. Orchestration  
   Kestra master pipeline runs all steps end-to-end  

## Data Visualization

View the Looker Studio dashboard here:  
👉 **https://datastudio.google.com/reporting/676a3203-5520-471a-823a-175573ebce8c**

The dashboard includes:

- Average Animal Stay Duration by Month  
- Distribution of Animal Outcomes (Top 5)  

## Setup & Reproduction

To reproduce this project, follow the instructions here:  
👉 [instructions.md](instructions.md)

## Author

Sebastian J.