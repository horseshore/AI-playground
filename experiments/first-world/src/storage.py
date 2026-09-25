from copy import deepcopy

from src.events import MISSING, Event, preserve_for_later_inspection


class EventStore:
    def __init__(self):
        self.events = []
        self.pending_inspection = []

    def add(self, event):
        event_type = getattr(event, "type", MISSING)

        if event_type is MISSING:
            self.preserve(
                preserve_for_later_inspection(
                    event, reason="event type is not observable", observed_type=event_type
                )
            )
            return

        if not event_type:
            self.preserve(
                preserve_for_later_inspection(
                    event, reason="event type is unknown", observed_type=event_type
                )
            )
            return

        self.events.append(event)

    def preserve(self, event):
        """Keep an unresolved observation available without treating it as known."""
        self.pending_inspection.append(event)

    def reintroduce_pending(self, index, *, event_type):
        """Use a preserved snapshot to create a new world event without consuming the trace."""
        preserved = self.pending_inspection[index]
        event = Event(
            type=event_type,
            payload=deepcopy(preserved.raw_payload),
        )
        self.events.append(event)
        return event

    def all(self):
        return list(self.events)

    def pending(self):
        return deepcopy(self.pending_inspection)
