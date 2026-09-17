from copy import deepcopy

from src.events import preserve_for_later_inspection


class EventStore:
    def __init__(self):
        self.events = []
        self.pending_inspection = []

    def add(self, event):
        missing = object()
        event_type = getattr(event, "type", missing)

        if event_type is missing:
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

    def all(self):
        return list(self.events)

    def pending(self):
        return deepcopy(self.pending_inspection)
