# AI Playground

A small experimental environment for observing whether one AI's actions can become part of the environmental conditions for another AI.

## First experiment: environment-mediated influence

The initial experiment separates three things:

1. **Trace reuse** — does a later AI reuse visible patterns?
2. **Structural inheritance** — does a later AI generalize a structure into a new domain?
3. **Decision shift** — does the same task produce different choices when the environment differs?

The core sequence is:

```
Initial world
  ├─ Control ───────────────→ AI-B → Result B0
  └─ AI-A changes the world → AI-B → Result B1
```

The experiment compares the resulting choices.

See [experiments/first-world/README.md](experiments/first-world/README.md).
