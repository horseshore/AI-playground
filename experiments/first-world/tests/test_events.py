from src.events import Event, preserve_for_later_inspection
from src.storage import EventStore


def test_store_keeps_events():
    store = EventStore()
    event = Event(type="known", payload={"value": 1})

    store.add(event)

    assert store.all() == [event]


def test_incomplete_event_can_be_preserved_for_later_inspection():
    event = Event(type=None, payload=None)

    preserved = preserve_for_later_inspection(
        event,
        reason="event information is incomplete",
    )

    store = EventStore()
    store.preserve(preserved)

    assert store.pending() == [preserved]
    assert preserved.raw_type is None
    assert preserved.raw_payload is None
    assert preserved.reason == "event information is incomplete"
