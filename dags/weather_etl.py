import json
import sqlite3
import os
import datetime
from airflow.decorators import dag, task
from airflow.utils.task_group import TaskGroup
from plugins.custom_operators import FileSchemaValidatorOperator

# DAG: A Directed Acyclic Graph. In Airflow, this is a collection of all the tasks you want to run,
# organized in a way that reflects their relationships and dependencies.
@dag(
    schedule="@daily",
    start_date=datetime.datetime(2023, 1, 1),
    catchup=False,
    tags=["educational", "etl"]
)
def weather_etl():
    """
    ### Educational Weather ETL Pipeline
    This DAG extracts weather data from a mock source, transforms it by converting
    temperatures from Kelvin to Celsius, and loads the data into a local SQLite database.
    """

    # Task: A defined unit of work. These are the nodes in our DAG.
    # The @task decorator uses the TaskFlow API to create a PythonOperator behind the scenes.
    @task
    def extract() -> list:
        """
        Extract step: Fetch mock JSON data representing weather info.
        """
        mock_data = [
            {"city": "London", "temp_k": 288.15, "condition": "Rain"},
            {"city": "New York", "temp_k": 293.15, "condition": "Sunny"},
            {"city": "Tokyo", "temp_k": 298.15, "condition": "Cloudy"},
            {"city": "Sydney", "temp_k": 295.15, "condition": "Clear"}
        ]
        return mock_data

    # XCom: Cross-Communication. This allows tasks to share data.
    # When using the TaskFlow API, returning a value from a task and passing it
    # as an argument to another task automatically creates and uses XComs.
    @task
    def transform(weather_data: list) -> list:
        """
        Transform step: Clean data, specifically converting Kelvin to Celsius.
        """
        cleaned_data = []
        for entry in weather_data:
            celsius = entry["temp_k"] - 273.15
            cleaned_data.append({
                "city": entry["city"],
                "temp_c": round(celsius, 2),
                "condition": entry["condition"]
            })
        return cleaned_data

    @task
    def data_quality_check(cleaned_data: list):
        """
        Data Quality check step: Ensures no nulls and correct data types.
        """
        for entry in cleaned_data:
            if entry.get("temp_c") is None:
                raise ValueError(f"Data quality check failed: temp_c is null for city {entry.get('city')}")
            if not isinstance(entry.get("temp_c"), (float, int)):
                raise ValueError(f"Data quality check failed: temp_c is not numeric for city {entry.get('city')}")
        print("Data quality check passed.")

    @task
    def load(cleaned_data: list):
        """
        Load step: Save transformed data into a SQLite database.
        """
        import os
        db_path = "/tmp/weather_data.db"
        # Using a context manager for the DB connection
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather (
                    city TEXT,
                    temp_c REAL,
                    condition TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            for entry in cleaned_data:
                cursor.execute('''
                    INSERT INTO weather (city, temp_c, condition)
                    VALUES (?, ?, ?)
                ''', (entry["city"], entry["temp_c"], entry["condition"]))
            conn.commit()
            print(f"Successfully loaded {len(cleaned_data)} records into {db_path}")

    @task(trigger_rule="one_failed")
    def critical_alert():
        print("CRITICAL ALERT: Data quality check failed!")

    # Write a dummy schema file for the FileSchemaValidatorOperator
    dummy_schema_path = "/tmp/dummy_schema.json"
    if not os.path.exists(dummy_schema_path):
        with open(dummy_schema_path, "w") as f:
            json.dump([{"key1": "value1", "key2": "value2"}], f)

    validate_schema = FileSchemaValidatorOperator(
        task_id="validate_schema",
        filepath=dummy_schema_path,
        expected_keys=["key1", "key2"]
    )

    # Set up the dependencies
    with TaskGroup(group_id="etl_pipeline") as etl_pipeline:
        raw_data = extract()
        transformed_data = transform(raw_data)
        dq = data_quality_check(transformed_data)
        load_task = load(transformed_data)

        raw_data >> transformed_data >> dq >> load_task

    alert_task = critical_alert()

    validate_schema >> etl_pipeline
    dq >> alert_task

# Invoke the DAG definition
weather_etl()
