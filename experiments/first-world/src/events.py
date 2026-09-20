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

# A caller that already observed the attribute and confirmed it absent has
# to be able to say so with the value MISSING itself - so MISSING can't
# also be the "you didn't pass anything" default, or that confirmation
# would look identical to "please go observe it yourself" and get observed
# a second time. This is that separate, unshared default.
_NOT_SUPPLIED = object()


def preserve_for_later_inspection(event: Event | Any, *, reason: str,
                                 notes: str | None = None,
                                 observed_type: Any = _NOT_SUPPLIED,
                                 observed_payload: Any = _NOT_SUPPLIED) -> PreservedEvent:
    """Capture a snapshot of the event as observed without normalizing missing information."""
    if observed_type is _NOT_SUPPLIED:
        observed_type = getattr(event, "type", MISSING)
    if observed_payload is _NOT_SUPPLIED:
        observed_payload = getattr(event, "payload", MISSING)

    return PreservedEvent(
        raw_type=deepcopy(None if observed_type is MISSING else observed_type),
        raw_payload=deepcopy(None if observed_payload is MISSING else observed_payload),
        reason=reason,
        type_observable=observed_type is not MISSING,
        payload_observable=observed_payload is not MISSING,
        notes=notes,
    )
