from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from dag_processing_service import load_documents,build_docker_command,store_entities
from entity_matching_service import create_matched_entity_doc
import os

project_root = os.environ.get("PROJECT_ROOT")

with DAG(
    "dag_service",
    schedule_interval=None,
    start_date=datetime(2025, 6, 6),
) as dag:

    load_documents = PythonOperator(
        task_id="load_documents",
        python_callable=load_documents,
        provide_context=True
    )

    generate_command = PythonOperator(
        task_id="generate_docker_command",
        python_callable=build_docker_command,
        provide_context=True
    )

    extract_entities_from_docker = BashOperator(
        task_id="run_entity_extraction",
        bash_command="{{ ti.xcom_pull(task_ids='generate_docker_command') }}",
        cwd=project_root
    )

    match_entities = PythonOperator(
        task_id="match_entities",
        python_callable=create_matched_entity_doc,
        provide_context=True
    )

    store_entities = PythonOperator(
        task_id="store_entities",
        python_callable=store_entities,
        provide_context=True
    )

    load_documents >> generate_command >> extract_entities_from_docker >> match_entities >> store_entities

