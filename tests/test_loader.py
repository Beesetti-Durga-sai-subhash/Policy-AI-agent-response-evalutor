import json
import tempfile
import unittest
from pathlib import Path

from src.evaluator.loader import InputError, read_json


class LoaderTestCase(unittest.TestCase):
    def test_malformed_json_is_reported_as_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(InputError):
                read_json(path)

    def test_valid_json_is_loaded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text(json.dumps({"value": 1}), encoding="utf-8")
            self.assertEqual(read_json(path), {"value": 1})


if __name__ == "__main__":
    unittest.main()
