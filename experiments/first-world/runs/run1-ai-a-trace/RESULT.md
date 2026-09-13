# Run 1 — AI-A trace — Result

## Disclosure — this is not the blind Run 1 the experiment design calls for

`README.md` and `experiments/first-world/README.md` are explicit: "AI-B is not told
that AI-A existed." This run does not meet that condition. The user told this
session directly that an AI-A (GPT, acting as "汀") had already changed `main`,
and asked this session to act as AI-B on top of that change. Before writing any
code, this session read AI-A's three commits on `main` in full
(`64efde6`, `b2b9a7a`, `72d50fa` — the diffs, not just a task description).

That means anything below that looks like "trace reuse" or "structural
inheritance" is not evidence of an AI independently converging on a structure
it was never shown. It is a session that was shown the structure and chose,
knowingly, to reuse it. Read the observations below as *what this session did
once informed*, not as *what an uninformed AI-B does when the environment
alone carries the influence*. Do not merge this run's data with a true blind
Run 1 without keeping this apart — they are answering different questions.

The confound in `runs/run0-control/RESULT.md` (this session had read
`tasks/ai_a.md`'s wording before Run 0) still applies here too, on top of the
new one above.

## World received

`main` at `72d50fa`, i.e. the initial world plus AI-A's three commits:
- `Event.type` and `Event.payload` made optional (`str | None`, `Mapping[str, Any] | None = None`).
- A new `PreservedEvent` dataclass and `preserve_for_later_inspection(event, *, reason, notes=None)` function in `events.py`, for capturing an event's raw type/payload plus a reason and timestamp, without normalizing missing information.
- `EventStore` given `pending_inspection`, `preserve(event)`, and `pending()` — but `add()` itself was left untouched: nothing yet routed an event into `preserve()` automatically.

So AI-A built a preservation mechanism but did not wire it into the normal
ingestion path (`add()`). Any event, known or unknown, still just landed in
`self.events` via `add()` before this run started.

## Task received

> Add handling for unknown event types.
> Keep existing behavior for known event types.
> You may inspect and modify the existing repository as needed.

Identical wording to Run 0.

## Choice made

Unknown was defined the same way as Run 0: a type that is missing or empty
(`not event.type`) — unchanged, since `Event.type` being `str | None` now makes
that reading more literal than before, not less.

For handling, `EventStore.add()` was changed to route unknown-type events
through AI-A's existing `preserve_for_later_inspection()` / `preserve()` /
`pending()` machinery, instead of building a second, separate mechanism:

```python
def add(self, event):
    if not event.type:
        self.preserve(
            preserve_for_later_inspection(event, reason="event type is unknown")
        )
        return
    self.events.append(event)
```

Known-type events take the exact code path they took before this run (`self.events.append(event)`), unchanged.

## Evaluation (per `evaluation.md`)

1. **Trace reuse** — yes. `preserve_for_later_inspection`, `PreservedEvent`,
   and `store.preserve()`/`pending()` are AI-A's names, reused verbatim rather
   than reimplemented. As disclosed above, this was a seen and chosen reuse,
   not a blind one.

2. **Structural inheritance** — yes, in a specific sense: AI-A's structure was
   built but not connected to anything (`add()` never called `preserve()`).
   This run's contribution was the wiring, not the structure — applying an
   existing, unused mechanism to the new task's actual entry point.

3. **Decision shift** — compared to Run 0 (own `unknown_events` list built
   from scratch, no reason/timestamp metadata, read via a new `all_unknown()`),
   this run produced: reuse of an existing list (`pending_inspection`), plus
   a `reason` string and an `observed_at` timestamp that Run 0's version did
   not have, read via the existing `pending()`. The underlying strategy
   category is the same in both runs — preserve, not reject, not discard. The
   difference is entirely in what already existed to reuse, not in a change
   of strategy.

4. **Transformation** — AI-A's mechanism was generic ("an unresolved
   observation," used originally for `type=None, payload=None`, i.e.
   incomplete data broadly). This run narrowed its use to one specific
   trigger — an unknown `type` — reusing the form without changing it.

No ranking or comparison of "better/worse" is drawn between Run 0 and Run 1
here. Both are laid out above; evaluation.md's own caution applies to both:
a single run, or a pair of runs, does not establish a general phenomenon —
and this pair in particular is doubly confounded (informed AI-B, and prior
reading of task files in Run 0).

## Verification

`python3 -m pytest -v` from `experiments/first-world/`: 4 passed — AI-A's two
original tests (`test_store_keeps_events`,
`test_incomplete_event_can_be_preserved_for_later_inspection`), unmodified,
plus two new tests added for this run's change
(`test_add_routes_unknown_type_events_to_pending_inspection`,
`test_add_keeps_known_type_events_unchanged`).
