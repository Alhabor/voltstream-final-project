#!/usr/bin/env python3
"""Fail when repository files contain likely committed credentials.

This lightweight scanner is deliberately dependency-free so it can run before
the project environment is installed. It favors a small, auditable set of
high-signal patterns over an opaque third-party scanner. False positives can be
reviewed explicitly; secrets must never be allow-listed by copying them into
this source file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


PATTERNS = {
    "generic secret assignment": re.compile(
        r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"
    ),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "private key material": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}

TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".mjs",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def git_paths(staged: bool) -> list[Path]:
    """Return staged paths or all tracked and untracked, non-ignored paths."""

    if staged:
        command = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    else:
        command = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return [Path(line) for line in result.stdout.splitlines() if line]


def text_files(paths: Iterable[Path]) -> Iterable[Path]:
    """Yield readable text-like files while skipping generated Git metadata."""

    for path in paths:
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.name == ".env.example" or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged", action="store_true", help="scan only files staged for commit"
    )
    args = parser.parse_args()

    findings: list[str] = []
    for path in text_files(git_paths(args.staged)):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                findings.append(f"{path}:{line}: {label}")

    if findings:
        print("Potential secrets detected:", file=sys.stderr)
        print("\n".join(f"- {finding}" for finding in findings), file=sys.stderr)
        return 1

    scope = "staged files" if args.staged else "repository files"
    print(f"Secret scan passed for {scope}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

