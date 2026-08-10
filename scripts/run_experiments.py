#!/usr/bin/env python3
"""Run one registered VoltStream strategy and persist raw evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from voltstream.experiment_runner import STRATEGIES, ExperimentRunner  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Stable output folder name")
    parser.add_argument("--strategy", required=True, choices=STRATEGIES)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse completed per-case artifacts in an interrupted strategy",
    )
    args = parser.parse_args()

    output = ExperimentRunner(ROOT, args.run_id).run(args.strategy, resume=args.resume)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
