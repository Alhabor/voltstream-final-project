import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from voltstream.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_machine_readable_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "submission.json"
            input_path.write_text(
                json.dumps(
                    {
                        "station_id": "CE-CLI-1",
                        "address": "1 CLI Way New York NY 10001",
                        "charger_level": "L2",
                        "ports": 2,
                        "power": "7.2 kW",
                        "source_record_id": "CLI-ROW-1",
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([str(input_path), "--source", "cli-test"])

        output = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(output["source_name"], "cli-test")
        self.assertEqual(output["records"][0]["decision"], "ACCEPT")


if __name__ == "__main__":
    unittest.main()
