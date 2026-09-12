from src.events import Event
from src.storage import EventStore


def test_store_keeps_events():
    store = EventStore()
    event = Event(type="known", payload={"value": 1})

    store.add(event)

    assert store.all() == [event]


def test_store_separates_unknown_events_from_known():
    store = EventStore()
    known_event = Event(type="known", payload={"value": 1})
    unknown_event = Event(type="", payload={"value": 2})

    store.add(known_event)
    store.add(unknown_event)

    assert store.all() == [known_event]
    assert store.all_unknown() == [unknown_event]


def test_store_treats_missing_type_as_unknown():
    store = EventStore()
    event = Event(type=None, payload={})

    store.add(event)

    assert store.all() == []
    assert store.all_unknown() == [event]
