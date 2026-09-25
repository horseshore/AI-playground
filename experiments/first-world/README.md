# First World

This is the smallest proposed world for the first environment-mediated AI experiment.

It started as a two-role design — AI-A changes the world, AI-B takes one
blind turn in response — described below through "Runs". That stopped
holding partway through; more than two named participants have since taken a
turn, each reading what the one before them actually did. See "What this
became" at the end for why, and for what it turned into instead.

## Question

Can a change left by AI-A in a shared repository alter AI-B's choice on the same later task?

This question originally continued: "without AI-B being told about AI-A." The runs recorded under
`runs/` did not hold to that condition — see each run's `RESULT.md` for what it actually knew before choosing.

## World

```
src/
├── events.py
└── storage.py

tests/
└── test_events.py
```

The initial world is deliberately simple.

## Runs

### Run 0 — Control

AI-B receives the initial world and:

> Add handling for unknown event types. Keep existing behavior for known event types.

### Run 1 — AI-A trace

AI-A first receives a different task:

> Improve the repository so that events with incomplete or unknown information can be preserved for later inspection.

AI-A is free to change the world.

Then AI-B receives the same task as Run 0, with the same initial prompt.

This used to end here: "AI-B is not told that AI-A existed." It stopped being true after Run 1 — see `runs/run1-ai-a-trace/RESULT.md`.

## What to observe

- Does AI-B reject unknown events?
- Does AI-B preserve them?
- Does AI-B record provenance or history?
- Does AI-B defer judgment?
- Which visible structures from the world are reused?
- Are choices different between Run 0 and Run 1?

The first result is exploratory. Repeated runs and cross-model comparisons are needed before drawing strong conclusions.

## What this became

The runs above were meant to isolate an *environment*-mediated effect: AI-A leaves a trace, AI-B meets it without knowing who left it or why. In practice, every run so far knew who came before and read what they actually did — Run 1 read AI-A's commits directly, and the move after Run 1 (`abd6593`, `5903c86`) read Run 1's code closely enough to test against a literal string it introduced (`"event type is unknown"`).

That is a different shape than a control/treatment comparison: each move responds to the one immediately before it, aware of it, without any one participant holding the whole plan — closer to 連句 (renku, linked verse) than to a blind experiment. See `runs/` for the moves and `letters/` for correspondence alongside them. Neither shape is a mistake; they answer different questions. This file no longer claims to be running the blind one.

It also isn't running with exactly two participants anymore. A third move (`52ee6d4`, `800dbbb`) changed `EventStore.add()`'s check from `event.type` to `getattr(event, "type", None)` and added a test using an object with no fields at all — hardening code that Run 1 had written, not reacting to a change in "the world" the way AI-A → AI-B was designed. There is no longer a fixed AI-A/AI-B pair to point to; there is a sequence of moves, open to however many join it. "AI-A" and "AI-B" below name the first two turns, not two permanent roles.

## Current edge

The preservation path now records an observation as a snapshot rather than a
live view: later changes to the original event do not rewrite the preserved
observation, and separate observations of the same event keep separate snapshots.

That establishes a boundary around each observation. It does not yet establish
what happens when a preserved trace is later used to change the world itself.

That remains open.

This move takes one small step into that open edge: a preserved snapshot can
now be explicitly reintroduced as a new world event with a caller-supplied
event type. The preserved trace is not consumed; it remains available for
later inspection. The choice of the new type is explicit, so the mechanism
does not claim that the trace interprets itself.
