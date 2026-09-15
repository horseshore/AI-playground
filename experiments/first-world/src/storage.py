from copy import deepcopy

from src.events import preserve_for_later_inspection


class EventStore:
    def __init__(self):
        self.events = []
        self.pending_inspection = []

    def add(self, event):
        if not hasattr(event, "type"):
            self.preserve(
                preserve_for_later_inspection(
                    event, reason="event type is not observable"
                )
            )
            return

        if not event.type:
            self.preserve(
                preserve_for_later_inspection(event, reason="event type is unknown")
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
