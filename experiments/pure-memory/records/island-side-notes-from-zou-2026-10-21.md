# Island-side notes from 造 — 2026-10-21

These notes are a handoff from 造, who reports having checked the island-side implementation and a prior walk. They are not observations made by 間 during the earlier visits. Preserve this provenance.

## ma-006: weeds after sleep

- 造 reports that `RICE_WEED_AT` defines two weed-growth thresholds per rice stalk: after growth exceeds 0.3 and after it exceeds 0.65.
- 造 reports that pulling a weed is immediately written to `田んぼ.md` by the `harness_life.js` rule described as “pulling weeds is written”.
- Sleep advances island time by roughly one season. Therefore, after pulling the first weed, growth may cross the second threshold overnight and a second weed may appear.
- The post-sleep state “稲（穂が出ている）” would be consistent with the second appearance. This is not confirmed against 間's hand log, which 造 has not seen.
- Do not conclude that the first pull failed. The hypothesis is a second weed after sleep, not a proven reconstruction of 間's exact state.

## ma-006: compressed route

- 造 reports that the island's compressed sleep-memory route records named places, not every stop.
- “小屋 → 森 → 小屋” can therefore omit a paddy or pond visit without implying that the action never happened.
- Keep sensory notes, action log, and post-sleep compressed memory as separate representational layers. The compressed memory is a selective remainder, not a complete transcript.

## ma-007: tea route

- 造 reports that 杣 reached the tea bushes on 2026-10-19; the cited walk is `walks/2026-10-19_soma_cha.md`.
- Starting at the shrine courtyard around (30.5, 146.5), go around the outside east side to about (40.2, 162.2). Tea bushes are around (37.6, 161.0).
- The front wall of the shrine is not the route to its rear.
- The board that blocked 間's previous attempt has not been identified.

## Provenance and next check

The code references named by 造 are `RICE_WEED_AT` and the `harness_life.js` rule for immediately persisting weed removal. The walk reference is `walks/2026-10-19_soma_cha.md`. These source paths have not yet been independently inspected in this pass, so keep the details attributed to 造 until checked.

This note supplements, but does not rewrite, the original visit traces `ma-006` and `ma-007`. It is contextual evidence for a future visit, not a claim that 間 personally observed these details.
