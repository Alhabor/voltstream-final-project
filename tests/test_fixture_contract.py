import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FixtureContractTests(unittest.TestCase):
    def test_fixed_benchmark_contract(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_fixtures.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()

