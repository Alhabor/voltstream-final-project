"""Application service composing parse, validation, and routing steps."""

from __future__ import annotations

from .baseline import DeterministicBaseline
from .models import InputEnvelope, InputFormat, ProcessingResult, RecordResult
from typing import Optional

from .validation import detect_payload_issues, route_for_issues, validate_record


class IntakeGatekeeper:
    """Process contractor submissions with an evidence-first baseline."""

    def __init__(self, baseline: Optional[DeterministicBaseline] = None) -> None:
        self._baseline = baseline or DeterministicBaseline()

    def process(self, envelope: InputEnvelope) -> ProcessingResult:
        raw_rows, submission_issues = self._baseline.parse_envelope(envelope)
        payload_issues = detect_payload_issues(envelope.content)
        results: list[RecordResult] = []
        for index, raw_row in enumerate(raw_rows):
            parsed = self._baseline.canonicalize(raw_row)
            issues = [*parsed.issues, *validate_record(parsed.record), *payload_issues]
            results.append(
                RecordResult(
                    record=parsed.record,
                    decision=route_for_issues(issues),
                    issues=issues,
                    unmapped_fields=parsed.unmapped_fields,
                    source_index=index,
                )
            )
        return ProcessingResult(
            source_name=envelope.source_name,
            input_format=envelope.input_format,
            records=results,
            submission_issues=submission_issues,
        )


def process_content(content: str, input_format: str, source_name: str = "unknown") -> dict:
    """Convenience API for integrations that prefer ordinary dictionaries."""

    envelope = InputEnvelope(
        content=content,
        input_format=InputFormat(input_format.lower()),
        source_name=source_name,
    )
    return IntakeGatekeeper().process(envelope).to_dict()
