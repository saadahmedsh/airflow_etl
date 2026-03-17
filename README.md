# Educational Apache Airflow Sandbox

This repository is an educational sandbox designed for learning and demonstrating Apache Airflow capabilities. It features ETL pipelines utilizing the modern TaskFlow API and runs locally via Docker Compose with the LocalExecutor.

## Project Structure

- `dags/`
  - `weather_etl.py`: A core ETL pipeline demonstrating extraction, transformation, and loading into a local SQLite database, organized using TaskGroups and featuring data quality checks.
  - `factory.py`: A script demonstrating dynamic DAG generation by reading metadata from `dag_config.json`.
  - `controller.py`: A controller DAG demonstrating advanced scheduling and dependencies using a FileSensor to trigger downstream DAGs via TriggerDagRunOperator.
- `plugins/`
  - `custom_operators.py`: Contains custom Airflow Operators, such as `FileSchemaValidatorOperator` for pre-ETL validation tasks.
- `tests/`
  - Unit tests implemented using the standard `unittest` framework.
- `ADVANCED_CONCEPTS.md`: Documentation on advanced Airflow features, such as customizing the XCom backend for large data transfers.
- `docker-compose.yaml`: Configuration for running the Airflow environment locally.

## Getting Started

To start the Airflow environment locally using Docker Compose, run:

```bash
docker-compose up -d
```

### Local Testing

Python dependencies can be installed using the standard `requirements.txt` file:

```bash
pip install -r requirements.txt
```

To run the unit tests, execute:

```bash
python -m unittest discover tests
```

Local testing of DAGs may require initializing the Airflow database:

```bash
airflow db migrate
```
