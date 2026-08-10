"""Typed domain models shared by parsing, validation, and routing.

The models intentionally distinguish raw input from canonical output. This prevents
callers from mistaking a model suggestion or a partially parsed record for accepted
source-of-truth data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class InputFormat(str, Enum):
    """Input types deliberately supported by the prototype."""

    CSV = "csv"
    JSON = "json"
    TEXT = "text"


class RouteDecision(str, Enum):
    """The only allowed downstream routing outcomes."""

    ACCEPT = "ACCEPT"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    REJECT = "REJECT"


class IssueSeverity(str, Enum):
    """Operational consequence of a validation issue."""

    WARNING = "warning"
    REVIEW = "review"
    REJECT = "reject"


@dataclass(frozen=True)
class InputEnvelope:
    """One contractor submission plus traceability metadata."""

    content: str
    input_format: InputFormat
    source_name: str = "unknown"

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")
        if not self.source_name.strip():
            raise ValueError("source_name cannot be blank")


@dataclass
class CanonicalRecord:
    """Small, defensible schema used by the capstone prototype.

    ``None`` means that a value was absent or could not be parsed safely. It must
    never be replaced with an invented default.
    """

    station_id: Optional[str] = None
    address: Optional[str] = None
    charger_level: Optional[str] = None
    port_count: Optional[int] = None
    power_kw: Optional[float] = None
    connector_type: Optional[str] = None
    operational_status: Optional[str] = None
    source_record_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Issue:
    """Machine-scoreable explanation of a parsing or validation problem."""

    code: str
    severity: IssueSeverity
    message: str
    field: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["severity"] = self.severity.value
        return result


@dataclass
class RecordResult:
    """Canonical candidate, evidence, and route for one input row."""

    record: CanonicalRecord
    decision: RouteDecision
    issues: list[Issue] = field(default_factory=list)
    unmapped_fields: list[str] = field(default_factory=list)
    source_index: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_index": self.source_index,
            "record": self.record.to_dict(),
            "decision": self.decision.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "unmapped_fields": self.unmapped_fields,
        }


@dataclass
class ProcessingResult:
    """Submission-level result; a valid submission may contain several rows."""

    source_name: str
    input_format: InputFormat
    records: list[RecordResult] = field(default_factory=list)
    submission_issues: list[Issue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "input_format": self.input_format.value,
            "records": [record.to_dict() for record in self.records],
            "submission_issues": [issue.to_dict() for issue in self.submission_issues],
        }
