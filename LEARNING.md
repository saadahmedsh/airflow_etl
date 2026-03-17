# Learning Apache Airflow

Welcome to the Airflow learning sandbox! This project is designed to help you understand the core concepts of Apache Airflow through a practical ETL (Extract, Transform, Load) pipeline example.

## Core Concepts

### Airflow Architecture
Apache Airflow is a platform to programmatically author, schedule, and monitor workflows. It consists of several key components:

1. **Scheduler**: The heart of Airflow. It reads the DAGs (Directed Acyclic Graphs), determines when tasks need to be run based on their dependencies and schedule, and sends tasks to the executor to be run.
2. **Webserver**: Provides a user interface (UI) to inspect, trigger, and debug the behavior of DAGs and tasks.
3. **Worker**: The process that actually executes the tasks. The number of workers and how they are managed depends on the configured Executor (e.g., LocalExecutor, CeleryExecutor).
4. **Metadata DB**: A database (usually PostgreSQL or MySQL) that stores the state of tasks, DAGs, connections, variables, and other Airflow metadata. The Scheduler, Webserver, and Workers all interact with this database.

### Important Principles

1. **Idempotency**: A crucial concept in data engineering. An idempotent task produces the same result regardless of how many times it is run. For example, if a task creates a table and inserts a day's worth of data, running it twice for the same day should not result in duplicate data or errors (e.g., using `INSERT ON CONFLICT` or `CREATE TABLE IF NOT EXISTS`). In Airflow, tasks should ideally be idempotent so that if a task fails and is retried, or if a DAG is rerun, the end state remains consistent and correct.

2. **Backfilling**: Airflow allows you to run a DAG for past dates. If you create a new DAG today but want it to process data starting from last month, you can configure the `start_date` to a date in the past and enable `catchup=True`. The scheduler will then "backfill" the missing DAG runs from the `start_date` up to the current date. Even with `catchup=False` (as in our example), you can manually trigger backfills via the CLI.

## Our Example: Weather ETL Pipeline

The code in `dags/weather_etl.py` demonstrates a simple ETL pipeline using Airflow's TaskFlow API.

* **Extract**: Fetches dummy JSON data representing weather conditions.
* **Transform**: Cleans the data, converting temperatures from Kelvin to Celsius.
* **Load**: Saves the transformed data into a local SQLite database (`/opt/airflow/dags/weather_data.db` inside the container, mapping to `./dags/weather_data.db` locally).

### Key Airflow Features Used:
* **`@dag` decorator**: Defines the DAG, its schedule, and its metadata.
* **`@task` decorator**: Turns a Python function into an Airflow task.
* **XComs (Cross-Communication)**: Notice how `extract()` returns data, which is then passed as an argument to `transform()`. Under the hood, Airflow uses XComs to pass this data between the isolated task instances.

## Step-by-Step Guide: Running the Pipeline

1.  **Start the Airflow Environment**:
    From the root of this repository, run the following command to start Airflow using Docker Compose:
    ```bash
    docker-compose up -d
    ```
    This will spin up the Postgres database, initialize the Airflow metadata database (`airflow-init`), and start the Webserver and Scheduler.

2.  **Access the Airflow UI**:
    Open your web browser and navigate to `http://localhost:8080`.
    *   **Username**: `airflow`
    *   **Password**: `airflow`

3.  **Find the DAG**:
    In the DAGs list, look for `weather_etl`. You can use the search bar or filter by the `educational` or `etl` tags.

4.  **Unpause the DAG**:
    By default, new DAGs are paused. Click the toggle switch on the left side of the `weather_etl` row to unpause it. Since it has a schedule, it might run automatically depending on the time.

5.  **Trigger the DAG Manually**:
    To manually start a run, click the "Play" button (a triangle icon) on the right side of the `weather_etl` row and select "Trigger DAG".

6.  **Monitor Execution**:
    Click on the DAG name (`weather_etl`) to view its details.
    *   Go to the **Graph** view to see the visual representation of your tasks (`extract` -> `transform` -> `load`) and watch their status change (Queued -> Running -> Success).
    *   Go to the **Grid** view to see a history of DAG runs.

7.  **Inspect Logs**:
    If a task fails (or even if it succeeds), you can click on the task instance in the Graph or Grid view and select "Logs" to see the output.

8.  **Verify the Output**:
    The final `load` task saves data to a SQLite database. Because we mapped the `dags` folder, you can inspect the file directly from your host machine if you have SQLite installed, or by exec-ing into the container:
    ```bash
    sqlite3 ./dags/weather_data.db "SELECT * FROM weather;"
    ```

9.  **Stop the Environment**:
    When you are done learning, you can stop the containers and clean up volumes:
    ```bash
    docker-compose down -v
    ```
