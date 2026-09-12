class EventStore:
    def __init__(self):
        self.events = []
        self.unknown_events = []

    def add(self, event):
        # There is no fixed vocabulary of type names to check against, so a
        # type is "known" whenever it carries any name at all; "unknown"
        # means the type itself is missing, not that the name is unfamiliar.
        if not event.type:
            self.unknown_events.append(event)
            return
        self.events.append(event)

    def all(self):
        return list(self.events)

    def all_unknown(self):
        return list(self.unknown_events)
