import unittest
from airflow.models import DagBag

class TestWeatherETLDAG(unittest.TestCase):
    def setUp(self):
        # Initialize DagBag to load the DAGs from the dags/ directory
        self.dagbag = DagBag(dag_folder='dags/', include_examples=False)

    def test_dag_loaded(self):
        """Test that the DAG can be loaded without import errors."""
        self.assertFalse(
            len(self.dagbag.import_errors) > 0,
            f"DAG import errors: {self.dagbag.import_errors}"
        )
        dag = self.dagbag.get_dag(dag_id='weather_etl')
        self.assertIsNotNone(dag)
        # We now have 6 tasks: validate_schema, extract, transform, data_quality_check, load, critical_alert
        self.assertEqual(len(dag.tasks), 6)

    def test_task_dependencies(self):
        """Test that the task dependencies are correct."""
        dag = self.dagbag.get_dag(dag_id='weather_etl')
        # Since extract, transform, data_quality_check, load are inside a task group,
        # their ids are prefixed with the task group id
        extract_task = dag.get_task('etl_pipeline.extract')
        transform_task = dag.get_task('etl_pipeline.transform')
        dq_task = dag.get_task('etl_pipeline.data_quality_check')
        load_task = dag.get_task('etl_pipeline.load')
        alert_task = dag.get_task('critical_alert')

        # extract -> transform
        self.assertTrue(transform_task.task_id in extract_task.downstream_task_ids)
        # transform -> dq
        self.assertTrue(dq_task.task_id in transform_task.downstream_task_ids)
        # dq -> load
        self.assertTrue(load_task.task_id in dq_task.downstream_task_ids)
        # dq -> critical_alert
        self.assertTrue(alert_task.task_id in dq_task.downstream_task_ids)

if __name__ == '__main__':
    unittest.main()
