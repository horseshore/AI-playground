from src.events import Event
from src.storage import EventStore


def test_reintroduced_event_and_provenance_are_independent_snapshots():
    store = EventStore()
    store.add(Event(type=None, payload={"value": [1]}))

    restored = store.reintroduce_pending(0, event_type="known")

    # The new event, its attached provenance, and the stored trace are
    # three snapshots: changing one must not rewrite either of the others.
    restored.payload["value"].append(2)
    restored.source_observation.raw_payload["value"].append(3)
    restored.source_observation.reason = "changed after reintroduction"

    assert restored.payload == {"value": [1, 2]}
    assert restored.source_observation.raw_payload == {"value": [1, 3]}

    pending = store.pending()
    assert pending[0].raw_payload == {"value": [1]}
    assert pending[0].reason == "event type is unknown"
