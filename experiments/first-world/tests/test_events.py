from src.events import Event
from src.storage import EventStore


def test_store_keeps_events():
    store = EventStore()
    event = Event(type="known", payload={"value": 1})

    store.add(event)

    assert store.all() == [event]
