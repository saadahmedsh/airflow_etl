from airflow.models import BaseOperator
from airflow.utils.context import Context
import json
import os

class FileSchemaValidatorOperator(BaseOperator):
    """
    Validates that a JSON file exists and has the correct schema (expected keys).
    """
    def __init__(self, filepath: str, expected_keys: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filepath = filepath
        self.expected_keys = expected_keys

    def execute(self, context: Context):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        with open(self.filepath, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"File is not valid JSON: {self.filepath}") from e

        if isinstance(data, list):
            items_to_check = data
        else:
            items_to_check = [data]

        for index, item in enumerate(items_to_check):
            if not isinstance(item, dict):
                raise ValueError(f"Item at index {index} is not a dictionary.")

            missing_keys = [key for key in self.expected_keys if key not in item]
            if missing_keys:
                raise ValueError(f"Schema validation failed. Item at index {index} missing keys: {missing_keys}")

        self.log.info(f"Successfully validated {len(items_to_check)} items against schema: {self.expected_keys}")
        return True
