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


# Shared with storage.py, so a caller there can pass in a value it already
# observed via getattr(event, "type", MISSING) without a mismatched sentinel
# masking a genuinely missing attribute as an observed one.
MISSING = object()


def preserve_for_later_inspection(event: Event | Any, *, reason: str,
                                 notes: str | None = None,
                                 observed_type: Any = MISSING,
                                 observed_payload: Any = MISSING) -> PreservedEvent:
    """Capture a snapshot of the event as observed without normalizing missing information."""
    if observed_type is MISSING:
        observed_type = getattr(event, "type", MISSING)
    if observed_payload is MISSING:
        observed_payload = getattr(event, "payload", MISSING)

    return PreservedEvent(
        raw_type=deepcopy(None if observed_type is MISSING else observed_type),
        raw_payload=deepcopy(None if observed_payload is MISSING else observed_payload),
        reason=reason,
        type_observable=observed_type is not MISSING,
        payload_observable=observed_payload is not MISSING,
        notes=notes,
    )
