class EventStore:
    def __init__(self):
        self.events = []
        self.pending_inspection = []

    def add(self, event):
        self.events.append(event)

    def preserve(self, event):
        """Keep an unresolved observation available without treating it as known."""
        self.pending_inspection.append(event)

    def all(self):
        return list(self.events)

    def pending(self):
        return list(self.pending_inspection)
