# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from google.cloud import bigquery
from pathlib import Path
from dotenv import load_dotenv

# Define the path to the .env file
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(env_file_path)

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=env_file_path)


def load_csv_to_bigquery(project_id, dataset_name, table_name, csv_filepath):
    """Loads a CSV file into a BigQuery table.

    Args:
        project_id: The ID of the Google Cloud project.
        dataset_name: The name of the BigQuery dataset.
        table_name: The name of the BigQuery table.
        csv_filepath: The path to the CSV file.
    """

    client = bigquery.Client(project=project_id)

    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip the header row
        autodetect=True,  # Automatically detect the schema
    )

    with open(csv_filepath, "rb") as source_file:
        job = client.load_table_from_file(
            source_file, table_ref, job_config=job_config
        )

    job.result()  # Wait for the job to complete

    print(f"Loaded {job.output_rows} rows into {dataset_name}.{table_name}")


def create_dataset_if_not_exists(project_id, dataset_name):
    """Creates a BigQuery dataset if it does not already exist.

    Args:
        project_id: The ID of the Google Cloud project.
        dataset_name: The name of the BigQuery dataset.
    """
    client = bigquery.Client(project=project_id)
    dataset_id = f"{project_id}.{dataset_name}"

    try:
        client.get_dataset(dataset_id)  # Make an API request.
        print(f"Dataset {dataset_id} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"  # Set the location (e.g., "US", "EU")
        dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
        print(f"Created dataset {dataset_id}")


def main():

    current_directory = os.getcwd()
    print(f"Current working directory: {current_directory}")

    """Main function to load CSV files into BigQuery."""
    project_id = os.getenv("BQ_PROJECT_ID")
    if not project_id:
        raise ValueError("BQ_PROJECT_ID environment variable not set.")

    dataset_name = "customer_subscription_data"
    customer_cases_csv_filepath = "insight_synergy/utils/data/customer_cases.csv"
    customer_info_csv_filepath = "insight_synergy/utils/data/customer_info.csv"
    customer_product_csv_filepath = "insight_synergy/utils/data/customer_product.csv"
    product_info_csv_filepath = "insight_synergy/utils/data/product_info.csv"

    # Create the dataset if it doesn't exist
    print("Creating dataset.")
    create_dataset_if_not_exists(project_id, dataset_name)

    # Load the customer_cases data
    print("Loading customer_cases table.")
    load_csv_to_bigquery(project_id, dataset_name, "customer_cases", customer_cases_csv_filepath)

    # Load the customer_info data
    print("Loading customer_info table.")
    load_csv_to_bigquery(project_id, dataset_name, "customer_info", customer_info_csv_filepath)

    # Load the customer_product data
    print("Loading customer_product table.")
    load_csv_to_bigquery(project_id, dataset_name, "customer_product", customer_product_csv_filepath)

    # Load the product_info data
    print("Loading product_info table.")
    load_csv_to_bigquery(project_id, dataset_name, "product_info", product_info_csv_filepath)


if __name__ == "__main__":
    main()
