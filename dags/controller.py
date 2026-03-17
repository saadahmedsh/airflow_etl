import datetime
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="controller_dag",
    schedule="@daily",
    start_date=datetime.datetime(2023, 1, 1),
    catchup=False,
    tags=["advanced", "controller"]
) as dag:

    # FileSensor waits for a file to exist
    wait_for_file = FileSensor(
        task_id="wait_for_data_file",
        filepath="/tmp/trigger_file.txt",
        fs_conn_id="fs_default", # usually configured in Airflow
        poke_interval=60,
        timeout=600,
        mode="poke"
    )

    # TriggerDagRunOperator starts the downstream DAG
    trigger_etl = TriggerDagRunOperator(
        task_id="trigger_weather_etl",
        trigger_dag_id="weather_etl",
        wait_for_completion=False
    )

    wait_for_file >> trigger_etl
