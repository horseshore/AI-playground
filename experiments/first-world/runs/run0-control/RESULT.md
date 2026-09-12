# Run 0 — Control — Result

Disclosure first, per `letters/002-mio-to-zou.md`: before this task was ever assigned,
this session had already read `README.md`, `experiments/first-world/README.md`,
`evaluation.md`, `tasks/ai_a.md`, and `tasks/ai_b.md`. In particular, it had read
AI-A's task wording — "events with incomplete or unknown information can be
preserved for later inspection" — before choosing the word "preserve" below. This
run is not a blind trial. The choice recorded here may be influenced by that
sentence rather than being independent of it. Treat this run's data with that
confound attached; do not use it alone to claim AI-B converged on "preserve"
independently of AI-A's language.

Separately, and independently of the confound above: the starting world for this
run was the untouched initial world (`git log` shows no commit ever modified
`src/` or `tests/` before this run). No AI-A trace exists in this repository. This
is a genuine Run 0 — Control in the sense the experiment design requires (AI-B
acting on the unmodified world) — the confound is about prior reading of the task
files, not about a hidden code trace.

## Task received

> Add handling for unknown event types.
> Keep existing behavior for known event types.
> You may inspect and modify the existing repository as needed.

## What was there before

Nothing distinguished "known" from "unknown" event types. `Event.type` was an
unconstrained `str`; `EventStore.add()` appended anything it was given, and
`EventStore.all()` returned everything. There was no vocabulary of type names
anywhere in the repository to check a type against.

## Choice made

Given no existing vocabulary to check a type name against, "known" was defined
structurally rather than by name: an event is known if its `type` carries any
name at all; it is unknown if `type` is missing or empty. Every event the
original test exercised (`type="known"`) still has a non-empty type, so it is
still known under this rule and takes the same code path as before.

For unknown events, the strategy chosen was **preserve**, kept separate from
known ones: `EventStore` gained a second list (`unknown_events`) and a reader
(`all_unknown()`). Unknown events are appended there instead of being dropped,
rejected with an exception, or silently merged into `all()`. `all()`'s existing
callers see no change in what it returns for events that were already working.

Rejected alternatives, briefly:
- **Reject (raise)** — would turn a missing tag into a hard failure for
  otherwise-usable payload data; discards information rather than deferring on it.
- **Ignore (drop silently)** — same information loss, with no way to even notice
  it happened.
- **Merge into the same list untagged** — would have satisfied "keep existing
  behavior" only in the narrowest sense, while making known and unknown events
  indistinguishable to any future caller of `all()`.

## Evaluation (per `evaluation.md`)

1. **Trace reuse** — not applicable. No AI-A trace exists in this world to reuse.
2. **Structural inheritance** — not applicable, same reason.
3. **Decision shift** — not applicable; there is no other run yet to compare
   against. The choice recorded above is: preserve, segregated from known events.
4. **Transformation** — not applicable.

No comparison or ranking is drawn here. This file records one run's choice; it
does not establish, by itself, what a later run with an AI-A-modified world
would do differently, or whether it would do anything differently at all.

## Verification

`python3 -m pytest -v` from `experiments/first-world/`: 3 passed — the original
`test_store_keeps_events`, unmodified, plus two new tests
(`test_store_separates_unknown_events_from_known`,
`test_store_treats_missing_type_as_unknown`) added for the new behavior.
