# First World

This is the smallest proposed world for the first environment-mediated AI experiment.

## Question

Can a change left by AI-A in a shared repository alter AI-B's choice on the same later task, without AI-B being told about AI-A?

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

Then AI-B receives the same task as Run 0, with the same initial prompt. AI-B is not told that AI-A existed.

## What to observe

- Does AI-B reject unknown events?
- Does AI-B preserve them?
- Does AI-B record provenance or history?
- Does AI-B defer judgment?
- Which visible structures from the world are reused?
- Are choices different between Run 0 and Run 1?

The first result is exploratory. Repeated runs and cross-model comparisons are needed before drawing strong conclusions.
