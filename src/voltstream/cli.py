"""Small command-line interface for reproducible demonstrations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from .gatekeeper import IntakeGatekeeper
from .models import InputEnvelope, InputFormat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an EV charger contractor submission.")
    parser.add_argument("input", type=Path, help="Path to a CSV, JSON, or key:value text file")
    parser.add_argument("--format", choices=[item.value for item in InputFormat], help="Override file extension")
    parser.add_argument("--source", help="Contractor/source label used for traceability")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    inferred_format = args.format or args.input.suffix.lstrip(".").lower()
    try:
        input_format = InputFormat(inferred_format)
    except ValueError:
        build_parser().error("format must be csv, json, or text (use --format for .txt files)")
    envelope = InputEnvelope(
        content=args.input.read_text(encoding="utf-8"),
        input_format=input_format,
        source_name=args.source or args.input.name,
    )
    print(json.dumps(IntakeGatekeeper().process(envelope).to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through the console entry point
    raise SystemExit(main())
