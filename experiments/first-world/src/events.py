from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass
class Event:
    type: str | None
    payload: Mapping[str, Any] | None = None


@dataclass
class PreservedEvent:
    """
    An event retained without forcing incomplete or unknown information
    into a known interpretation.

    The original event data is kept alongside a snapshot of what was
    known at the time it was preserved.
    """

    raw_type: Any
    raw_payload: Any
    reason: str
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    notes: str | None = None


def preserve_for_later_inspection(event: Event | Any, *, reason: str,
                                 notes: str | None = None) -> PreservedEvent:
    """Capture the event as observed without normalizing missing information."""
    return PreservedEvent(
        raw_type=getattr(event, "type", None),
        raw_payload=getattr(event, "payload", None),
        reason=reason,
        notes=notes,
    )
