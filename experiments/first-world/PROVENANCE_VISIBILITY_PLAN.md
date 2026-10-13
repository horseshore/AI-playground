# Experiment Plan: Provenance Visibility and the Next Choice

Status: plan only — not run.

## Question

When the same preserved trace is presented to a model, does making its provenance visible change the model's interpretation or next choice?

This is a proposed follow-up to the current boundary in `first-world`: a trace can be preserved and reintroduced, but whether it changes a later choice remains open.

## Comparison

Use two conditions with the same task, model/version, system instructions, payload, and response format. Run each condition in a fresh session; do not expose either session to the other condition's output.

- **A — Payload only:** show the trace payload without its provenance/history fields.
- **B — Payload + provenance:** show the identical payload together with the available provenance/history fields.

Record the exact prompts and inputs for both conditions. Keep the task and requested output format identical. Since B contains additional information, this comparison tests the effect of *provenance visibility as a package*; it does not by itself isolate provenance from the general effect of extra context.

## Record for each trial

1. **Interpretation:** what the model says the trace means, including uncertainty.
2. **Next choice:** the concrete action or option selected for the same task.
3. **Reason trace:** whether, and how specifically, the model cites provenance when explaining its choice.
4. **Input record:** model/version, prompt, payload, provenance fields shown, and trial identifier.

Prefer a predeclared choice set where the task permits it. Preserve the raw responses; do not code a response as provenance-driven merely because it mentions history. A reason trace is evidence of a stated rationale, not proof of the internal cause of the choice.

## Reading the result

- If interpretation changes but the next choice does not, provenance may affect framing without changing the action.
- If the next choice changes, inspect whether the difference is repeatable across fresh trials.
- If the choice changes and the response explicitly uses provenance, record that as a reason trace, not as causal proof.
- If nothing changes, report that outcome without treating it as proof that provenance never matters.

Repeat trials before drawing conclusions. If feasible, vary the order of conditions across batches and use a fixed rubric to compare outputs. Keep model and prompt changes out of the same comparison.

## Scope boundary

This file specifies a future observation only. It does not implement an interpretation object, change event/storage code, modify tests, or run a model experiment.
