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
        self.assertEqual(len(dag.tasks), 3)

    def test_task_dependencies(self):
        """Test that the task dependencies are correct."""
        dag = self.dagbag.get_dag(dag_id='weather_etl')
        extract_task = dag.get_task('extract')
        transform_task = dag.get_task('transform')
        load_task = dag.get_task('load')

        # extract -> transform
        self.assertTrue(transform_task.task_id in extract_task.downstream_task_ids)
        # transform -> load
        self.assertTrue(load_task.task_id in transform_task.downstream_task_ids)

if __name__ == '__main__':
    unittest.main()
