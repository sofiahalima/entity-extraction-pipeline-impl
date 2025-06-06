from pathlib import Path
import pandas as pd
from datetime import datetime
import logging
from entity_matching_service import create_matched_entity_doc
import os
from dotenv import load_dotenv

from schema.output_schema import entity_schema
import pandera.pandas as pa

load_dotenv()
project_root = os.environ.get("PROJECT_ROOT")

logger = logging.getLogger(__name__)


def load_documents(**context):
    """
        Load documents from the source, ex. csv from data directory
        and push it to context for shared access on docker service

    Args:
        context (dict): Context is passed so that values are passed between the tasks

    Returns:
        returns dataframe
    """
    logger.info("Loading documents...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    input_path = f"shared_volume/input_{timestamp}.csv"

    df = pd.read_csv("data/documents.csv")
    df.to_csv(input_path, index=False)

    # Push the filename to XCom
    context['ti'].xcom_push(key='input_filename', value=f"input_{timestamp}.csv")

    logger.info(f"Saved input CSV to {input_path}")

    return df


def build_docker_command(**context):
    """
        docker build command to load documents to shared access on docker service and
        generate command to execute the entity extraction

    Args:
        context (dict): Context is passed so that values are passed between the tasks

    Returns:
        returns command as str
    """
    logger.info("Running docker build...")
    filename = context['ti'].xcom_pull(task_ids='load_documents', key='input_filename')
    logger.info(f"[build_docker_command] Input filename: {filename}")
    timestamp = filename.replace("input_", "").replace(".csv", "")
    input_path = f"/shared/{filename}"
    output_path = f"/app/output/extracted_entities_{timestamp}.json"

    command = (
        f"docker-compose -f {project_root}/docker-compose.yml "
        f"run --rm ner_extractor python /app/run_extractor.py {input_path} {output_path}"
    )

    # Push output file name for next task
    context['ti'].xcom_push(key='output_filename', value=f"extracted_entities_{timestamp}.json")

    return command


def store_entities():
    """
     This function is used to store the final output of entity extraction with original document.
     For this project submission, it mimics the original concept of persisting the data
     to the database, so it can be used to further insights.

     Schema validation is done using the following schema:entity_schema

    """

    output_doc_path = f"{project_root}/output/output.csv"

    df_entities = create_matched_entity_doc()
    try:
        validated_df = entity_schema.validate(df_entities)
    except pa.errors.SchemaError as e:
        logger.error(f" Schema validation failed:{e}")
        raise
    validated_df.to_csv(output_doc_path, index=False)

    logger.info(f" Saved validated entity data to: {output_doc_path}")


# for testing
if __name__ == "__main__":
    store_entities()