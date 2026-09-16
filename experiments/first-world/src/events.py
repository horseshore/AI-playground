from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass
class Event:
    type: str | None = None
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
    type_observable: bool
    payload_observable: bool
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    notes: str | None = None


def preserve_for_later_inspection(event: Event | Any, *, reason: str,
                                 notes: str | None = None) -> PreservedEvent:
    """Capture a snapshot of the event as observed without normalizing missing information."""
    missing = object()
    observed_type = getattr(event, "type", missing)
    observed_payload = getattr(event, "payload", missing)
    return PreservedEvent(
        raw_type=deepcopy(None if observed_type is missing else observed_type),
        raw_payload=deepcopy(None if observed_payload is missing else observed_payload),
        reason=reason,
        type_observable=observed_type is not missing,
        payload_observable=observed_payload is not missing,
        notes=notes,
    )
