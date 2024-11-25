import logging
import traceback
import os
from google.cloud import bigquery
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

bq_path = os.getenv('BQ_SERVICE_ACCOUNT_KEY_PATH')


def dataframe_to_bigquery(dataframe, dataset_name, table_name):
    try:
        # Create a BigQuery client using credentials
        credentials = service_account.Credentials.from_service_account_file(
            bq_path,
        )
        client = bigquery.Client(credentials=credentials)

        # Define table_id
        table_id = f"{client.project}.{dataset_name}.{table_name}"
        
        # Extract the transaction numbers from the dataframe
        transaction_numbers = dataframe['transaction_number'].tolist()

        # Construct query to check if any transaction_number already exists in BigQuery
        query = f"""
        SELECT transaction_number
        FROM `{client.project}.{dataset_name}.{table_name}`
        WHERE transaction_number IN UNNEST(@transaction_numbers)
        LIMIT 1
        """
        
        # Run the query with the list of transaction numbers
        query_params = [
            bigquery.ArrayQueryParameter("transaction_numbers", "STRING", transaction_numbers)
        ]
        query_job = client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=query_params))
        result = query_job.result()

        # If the result is non-empty, that means at least one transaction_number exists
        if result.total_rows > 0:
            print("Yes, at least one transaction_number exists in BigQuery.")
            return 'found'
            # Optionally, update the dataframe to indicate existence if required
        else:
            # If the table does not exist, create one with the schema derived from the dataframe
            # Otherwise, it appends to the existing table
            job = client.load_table_from_dataframe(dataframe, table_id, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"))   

            # Wait for the load job to complete
            job.result()
            print("Data uploaded successfully.")
            return 'uploaded'
        
        
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error("Traceback: %s", traceback.format_exc())
