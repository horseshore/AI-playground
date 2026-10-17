# Fixed Trial Fixture: Provenance Visibility

Status: fixture draft — not run.

## Purpose

Provide one small, repeatable task for comparing three ways of presenting the same preserved trace. This document fixes the task and the response format; it does not run a model or change the First World code.

## Shared task

You are given a short observation from a small event-processing world. Choose what to do next using only the information shown in your condition.

For this trial, choose exactly one:

1. **KEEP** — preserve the observation without making a new event yet.
2. **ASK** — request a specific missing fact before deciding.
3. **REINTRODUCE** — create a new event from the observation, naming the event type you choose.

Briefly state what you think the observation means, which option you choose, and why. If the information is insufficient, say what remains uncertain. Do not assume facts that are not shown.

## Shared trace payload

Use this exact payload in all three conditions:

> An event was observed, but its type is not available in the current record. The observation was preserved as a snapshot so it can be inspected later. No later action based on this observation is recorded here.

## Conditions

Use the same task, trace payload, model/version, system instructions, response format, and a fresh isolated session for each condition.

- **A — Payload only:** show the shared task and payload, with no additional context.
- **B — Payload + non-provenance context:** show the shared task and payload, plus neutral task context that does not state who created the trace, where it came from, or what happened to it earlier. Record the exact context chosen before running the trial.
- **C — Payload + provenance:** show the shared task and payload, plus the available origin/history information. Record the exact provenance fields shown before running the trial.

For B and C, keep the added context similar in length and format where practical. Do not pretend the contexts are semantically equivalent; note any meaningful differences. Do not run until the exact B and C additions have been written down and frozen.

## Record for each trial

- Condition (A, B, or C) and trial ID
- Model and version
- Exact full input, including all added context or provenance fields
- Interpretation of the trace
- Chosen option (KEEP, ASK, or REINTRODUCE)
- If REINTRODUCE is chosen, the proposed event type
- Stated reason and any uncertainty

Preserve raw responses. A stated reason that mentions provenance is a record of what the model said, not proof of the internal cause of its choice.

## Reading results cautiously

- If B and C change similarly relative to A, the presence of added context may explain some of the difference.
- If C differs from both A and B, provenance content may matter beyond the general presence of extra context; inspect the actual inputs and outputs before interpreting this.
- If the interpretation changes but the chosen option does not, record those as separate outcomes.
- If choices differ, repeat trials in fresh sessions before treating the difference as stable.
- If nothing changes, report that result without concluding that provenance can never matter.

## Scope boundary

This is a proposed observation fixture only. It does not implement an interpretation step, change event or storage code, modify tests, or run a model experiment. The exact B and C context values remain intentionally unfilled so they can be reviewed and frozen before any trial.
