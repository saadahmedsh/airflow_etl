import json
import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
import os

config_path = os.path.join(os.path.dirname(__file__), "dag_config.json")

def create_dag(dag_id, schedule, description):
    with DAG(
        dag_id=dag_id,
        schedule=schedule,
        start_date=datetime.datetime(2023, 1, 1),
        catchup=False,
        description=description,
        tags=["dynamic"]
    ) as dag:
        start = EmptyOperator(task_id="start")
        end = EmptyOperator(task_id="end")
        start >> end
    return dag

try:
    with open(config_path, "r") as f:
        dag_configs = json.load(f)

    for config in dag_configs:
        dag_id = config.get("dag_id")
        schedule = config.get("schedule", "@daily")
        description = config.get("description", "A dynamically generated DAG")

        globals()[dag_id] = create_dag(dag_id, schedule, description)

except FileNotFoundError:
    print(f"Config file not found: {config_path}")
except json.JSONDecodeError:
    print(f"Error decoding JSON config file: {config_path}")
