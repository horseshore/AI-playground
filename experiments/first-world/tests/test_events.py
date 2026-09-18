from datetime import datetime, timezone

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
    assert preserved.type_observable is True
    assert preserved.payload_observable is True


def test_add_routes_unknown_type_events_to_pending_inspection():
    store = EventStore()
    event = Event(type=None, payload={"value": 1})

    store.add(event)

    assert store.all() == []
    pending = store.pending()
    assert len(pending) == 1
    assert pending[0].raw_type is None
    assert pending[0].raw_payload == {"value": 1}
    assert pending[0].reason == "event type is unknown"
    assert pending[0].type_observable is True
    assert pending[0].payload_observable is True


def test_add_keeps_known_type_events_unchanged():
    store = EventStore()
    event = Event(type="known", payload={"value": 1})

    store.add(event)

    assert store.all() == [event]
    assert store.pending() == []


def test_known_type_does_not_require_observable_payload():
    class TypeOnlyEvent:
        def __init__(self, type):
            self.type = type

    store = EventStore()
    event = TypeOnlyEvent(type="known")
    store.add(event)

    assert store.all() == [event]
    assert store.pending() == []


def test_known_type_does_not_access_unobservable_payload():
    class PayloadThatCannotBeObserved:
        type = "known"

        @property
        def payload(self):
            raise RuntimeError("payload is not observable")

    store = EventStore()
    event = PayloadThatCannotBeObserved()
    store.add(event)

    assert store.all() == [event]
    assert store.pending() == []


def test_incomplete_event_can_omit_type_at_construction():
    event = Event(payload={"value": 1})

    store = EventStore()
    store.add(event)

    pending = store.pending()
    assert len(pending) == 1
    assert pending[0].raw_type is None
    assert pending[0].raw_payload == {"value": 1}
    assert pending[0].reason == "event type is unknown"
    assert pending[0].type_observable is True
    assert pending[0].payload_observable is True


def test_event_without_observable_type_is_preserved():
    class OpaqueEvent:
        pass

    store = EventStore()
    event = OpaqueEvent()
    store.add(event)

    pending = store.pending()
    assert len(pending) == 1
    assert pending[0].raw_type is None
    assert pending[0].raw_payload is None
    assert pending[0].reason == "event type is not observable"
    assert pending[0].type_observable is False
    assert pending[0].payload_observable is False


def test_type_and_payload_observability_vary_independently():
    class TypeOnlyEvent:
        def __init__(self, type):
            self.type = type

    store = EventStore()
    event = TypeOnlyEvent(type=None)
    store.add(event)

    pending = store.pending()
    assert len(pending) == 1
    assert pending[0].reason == "event type is unknown"
    assert pending[0].type_observable is True
    assert pending[0].payload_observable is False


def test_preservation_records_when_the_observation_was_made():
    event = Event(type=None, payload={"value": 1})

    before = datetime.now(timezone.utc)
    preserved = preserve_for_later_inspection(
        event,
        reason="event information is incomplete",
    )
    after = datetime.now(timezone.utc)

    assert before <= preserved.observed_at <= after
    assert preserved.observed_at.tzinfo is timezone.utc


def test_pending_returns_copies_that_cannot_corrupt_the_store():
    store = EventStore()
    store.add(Event(type=None, payload={"value": 1}))

    pending = store.pending()
    pending[0].reason = "tampered"

    assert store.pending()[0].reason == "event type is unknown"


def test_preservation_keeps_a_snapshot_of_mutable_payload():
    payload = {"value": [1]}
    event = Event(type=None, payload=payload)

    preserved = preserve_for_later_inspection(
        event,
        reason="event information is incomplete",
    )
    payload["value"].append(2)

    assert preserved.raw_payload == {"value": [1]}


def test_preservation_observes_type_and_payload_only_once():
    class CountingEvent:
        def __init__(self):
            self.type_reads = 0
            self.payload_reads = 0

        @property
        def type(self):
            self.type_reads += 1
            return None

        @property
        def payload(self):
            self.payload_reads += 1
            return {"value": 1}

    event = CountingEvent()

    preserve_for_later_inspection(event, reason="event type is unknown")

    assert event.type_reads == 1
    assert event.payload_reads == 1


def test_known_type_is_observed_only_once():
    class SingleObservationEvent:
        def __init__(self):
            self.type_reads = 0

        @property
        def type(self):
            self.type_reads += 1
            return "known"

    store = EventStore()
    event = SingleObservationEvent()

    store.add(event)

    assert store.all() == [event]
    assert event.type_reads == 1


def test_unknown_type_is_not_reobserved_when_preserved():
    class SingleObservationUnknownEvent:
        def __init__(self):
            self.type_reads = 0

        @property
        def type(self):
            self.type_reads += 1
            return None

    store = EventStore()
    event = SingleObservationUnknownEvent()

    store.add(event)

    assert event.type_reads == 1
    assert store.pending()[0].raw_type is None


def test_unknown_type_routing_uses_the_first_observation():
    class ChangingTypeEvent:
        def __init__(self):
            self.type_reads = 0

        @property
        def type(self):
            self.type_reads += 1
            return None if self.type_reads == 1 else "known"

    store = EventStore()
    event = ChangingTypeEvent()

    store.add(event)

    assert event.type_reads == 1
    assert store.all() == []
    assert store.pending()[0].raw_type is None
    assert store.pending()[0].reason == "event type is unknown"
