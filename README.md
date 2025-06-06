#  Entity Extraction Pipeline (GLiNER + Airflow)

This repository contains an end-to-end entity extraction pipeline that processes documents to extract and match named entities using a fine-tuned deep learning model. It leverages **spaCy**, **GLiNER**, **Airflow**, **Docker**, and **Parquet/SQLite** for scalable, modular, and efficient processing.

---

##  Features

- ✅ Named Entity Recognition with **GLiNER**
- ✅ Dockerized NER microservice for isolation and caching
- ✅ Entity matching with alias disambiguation
- ✅ DAG-based orchestration using **Apache Airflow**
- ✅ Persistent model cache via volume mounting
- ✅ Intermediate and final results stored as **Parquet/JSON/CSV** (or SQLite)
- ✅ Fully extensible for online inference or REST APIs

---

## Architecture

```mermaid
graph TD
    A[Load Documents (CSV)] --> B[Entity Extraction (Docker)]
    B --> C[Entity Matching (Alias Table)]
    C --> D[Store to Parquet/SQLite]

entity-extraction-pipeline-impl/
│
├── dags/                      # Airflow DAGs
      ├── dag_service.py       # DAG starter service
      ├── data_processing_service.py
      ├── data_matching_service.py   
├── docker_service/          # Docker context for NER service
      ├── extractor.py       
      ├── Dockerfile
      ├── run_extractor.py   # Docker entrypoint: NER + output
      └── requirements.txt       
├── shared_volume/           # Input document CSVs shared accross docker
├── extracted_entity/        # extracted Input JSON files received from docker
├── model_cache/             # Cached GLiNER models (mounted)
├── data/                    # Source document and alias CSVs
├── output/                  # Output result to be stored in DB
├── docker-compose.yml
```

**DAG & Docker service are build in different directory, so that its easy for docker_service to be scaled in future

## How It Works
**load_documents** : Loads document CSV and saves a timestamped copy to shared_volume/.

**build_docker_command** : Constructs the Docker Compose command with dynamic file paths.

**run_entity_extraction** : Executes the GLiNER NER model in a Docker container using mounted volumes.

**match_entities** : Matches extracted entities against aliases (from entity_aliases.csv).

**store_entities** : Saves final structured output as a Parquet file.

## Setup & Run
1. Clear below folders
   - output
   - shared_volume
   - extracted_entity
     
2. Build Docker Image
   - docker-compose build ner_extractor

3. Start Airflow
    - export AIRFLOW_HOME=$(pwd)/airflow_home"
    - airflow db init
    - airflow webserver --port 8080
    
    - airflow scheduler (in another terminal)

      --- OR
      
    - uv run --env-file .env airflow standalone

4. Trigger DAG
    - via UI

<img width="1488" alt="Screenshot 2025-06-06 at 10 36 36 AM" src="https://github.com/user-attachments/assets/45e7b761-7649-4bf7-becd-1068f5bac491" />

 Sample Command for Manual Run
    - docker-compose run --rm ner_extractor /shared/input_test.csv /app/output/output_test.json

## Model Caching
Model is cached at:
 - /root/.cache/huggingface/
Mapped to host via:
 - ./model_cache:/root/.cache/huggingface
   
--This ensures fast reuse of GLiNER weights without redownloading.

<img width="1029" alt="Screenshot 2025-06-06 at 10 41 00 AM" src="https://github.com/user-attachments/assets/713b1da1-9434-4117-8706-027d68373f4d" />

- shows cache logs during task execution.

## Output Format
    -uuid (from document)

    -title, content, date, etc. (from document)

    -entities: a list of:       (from extracted entity & aliases table)

          -entity_text, 
          -entity_type, 
          -start_pos,
          -end_pos
          -is_matched, 
          -matched_entity_id, 
          -matched_entity_name




