import ast
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import os
import logging
from rich import json
from entity_matching_service import create_matched_entity_doc

# timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
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

    print(f"Saved input CSV to {input_path}")

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
    filename = context['ti'].xcom_pull(task_ids='load_documents', key='input_filename')
    timestamp = filename.replace("input_", "").replace(".csv", "")
    input_path = f"/shared/{filename}"
    output_path = f"/app/output/extracted_entities_{timestamp}.json"

    # command = (
    #     f"docker-compose -f /Users/sofiahalima/PycharmProjects/entity-extraction-pipeline-impl/docker-compose.yml "
    #     f"run --rm ner_extractor {input_path} {output_path}"
    # )

    command = (
        f"docker-compose -f /Users/sofiahalima/PycharmProjects/entity-extraction-pipeline-impl/docker-compose.yml "
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

    """
    project_root = Path(__file__).parent.parent
    output_doc_path = project_root / 'output' / 'output.csv'
    logger.info("Storing output to {}".format(output_doc_path))
    create_matched_entity_doc().to_csv(output_doc_path, index=False)
    print(f" Entity matching results written to {output_doc_path}")


def extract_entities():
    logger.info("Sending request to NER service to get extracted entities")

# def load_aliases(path):
#     df = pd.read_csv(path)
#     df["aliases"] = df["aliases"].apply(ast.literal_eval)
#     return [EntityAlias(**row) for _, row in df.iterrows()]
#
#
# def match_entity(entity_text, entity_type, alias_table):
#     for alias in alias_table:
#         if alias.entity_type != entity_type:
#             continue
#         if entity_text == alias.name or entity_text in alias.aliases:
#             return alias
#     return None
#
#
# def process_entities(doc_path, alias_csv, json_file, output_path):
#     logger.info("Processing entities after matching with aliases")
#
#     alias_table = load_aliases(alias_csv)
#
#     docs = pd.read_csv(doc_path)
#
#     with open(json_file, 'r') as f:
#         entity_data = json.load(f)
#
#     output_rows = []
#
#     for entry in entity_data:
#         doc_id = entry["uuid"]
#         doc_base = docs.get(doc_id)
#         matched_entities = []
#
#         for ent in entry.get("entities", []):
#             match = match_entity(ent["text"], ent["label"], alias_table)
#             matched_entities.append(EntityMatch(
#                 entity_type=ent["label"],
#                 entity_text=ent["text"],
#                 start_pos=ent["start"],
#                 end_pos=ent["end"],
#                 is_matched=bool(match),
#                 matched_entity_id=match.id if match else None,
#                 matched_entity_name=match.name if match else None
#             ))
#
#         output_doc = EntityOutput(
#             uuid=doc_base["uuid"],
#             title=doc_base.get("title"),
#             content=doc_base.get("content"),
#             publication_date=doc_base.get("date"),
#             inserted_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             source=doc_base["url"],
#             entities=matched_entities)
#
#         output_rows.append(output_doc.dict())
#
#     df = pd.DataFrame(output_rows)
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     df.to_parquet(output_path, index=False)
#     print(f"Entity matching results written to {output_path}")
