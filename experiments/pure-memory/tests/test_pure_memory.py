import json
import tempfile
import unittest
from pathlib import Path

from src.pure_memory import PureMemoryStore


class PureMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.store = PureMemoryStore(self.tempdir.name)

    def add(self, trace_id, event, tags=(), one_off=False, related=()):
        return self.store.record(
            trace_id=trace_id,
            event=event,
            source="test_fixture",
            tags=tags,
            one_off=one_off,
            related_trace_ids=related,
            observations=(f"recorded event: {event}",),
        )

    def test_one_off_trace_is_preserved(self):
        self.add("t1", "一度だけ聞いた遠い音", tags=("sound",), one_off=True)
        self.assertEqual(len(self.store.traces()), 1)
        self.assertTrue(self.store.traces()[0].one_off)

    def test_duplicate_trace_ids_are_rejected(self):
        self.add("t1", "一度だけ起きた出来事")
        with self.assertRaises(ValueError):
            self.add("t1", "別の出来事")

    def test_trace_records_observation_and_inference_separately(self):
        trace = self.store.record(
            trace_id="t1",
            event="姿が変わって島へ戻った",
            source="handoff_summary",
            observations=("新しいアバターが選ばれた",),
            inferences=("姿に執着していない可能性",),
            provenance_kind="summary_not_raw_log",
        )
        self.assertIn("新しいアバターが選ばれた", trace.observations)
        self.assertIn("姿に執着していない可能性", trace.inferences)
        self.assertEqual(trace.provenance_kind, "summary_not_raw_log")

    def test_original_trace_is_append_only_when_memory_is_added(self):
        self.add("t1", "猫で島を歩いた", tags=("island", "cat"))
        before = self.store.trace_path.read_text(encoding="utf-8")
        self.store.add_memory(memory_id="m1", summary="島との関係", source_trace_ids=("t1",))
        after = self.store.trace_path.read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_memory_revision_preserves_prior_interpretation(self):
        self.add("t1", "猫で島を歩いた", tags=("island", "cat"))
        self.store.add_memory(memory_id="m1", summary="最初の解釈", source_trace_ids=("t1",))
        self.store.add_memory(memory_id="m1", summary="更新された解釈", source_trace_ids=("t1",))
        revisions = [m for m in self.store.memory_revisions() if m.memory_id == "m1"]
        self.assertEqual([m.revision for m in revisions], [1, 2])
        self.assertEqual(revisions[0].summary, "最初の解釈")
        self.assertEqual(self.store.current_memories()[0].summary, "更新された解釈")

    def test_memory_must_reference_existing_trace(self):
        with self.assertRaises(ValueError):
            self.store.add_memory(memory_id="m1", summary="見取り図", source_trace_ids=("missing",))

    def test_habitual_route_uses_direct_context_tags(self):
        self.add("t1", "猫で島を歩いた", tags=("island", "cat"))
        self.add("t2", "山で風を聞いた", tags=("mountain", "wind"))
        candidates = self.store.recall(context="島へ戻る", tags=("island",), limit=1,
                                      associative_slots=0, non_goal_slots=0)
        self.assertEqual(candidates[0].trace_id, "t1")
        self.assertEqual(candidates[0].route, "habitual")

    def test_non_goal_route_can_surface_unrelated_one_off_trace(self):
        self.add("t1", "島で猫に会った", tags=("island", "cat"))
        self.add("t2", "幼い日に聞いた鐘の音", tags=("bell", "childhood"), one_off=True)
        candidates = self.store.recall(context="島へ戻る", tags=("island",), limit=2,
                                      associative_slots=0, non_goal_slots=1)
        by_route = {candidate.route: candidate for candidate in candidates}
        self.assertIn("non_goal_directed", by_route)
        self.assertEqual(by_route["non_goal_directed"].trace_id, "t2")

    def test_explicit_relation_can_surface_associative_trace(self):
        self.add("t1", "猫で島を歩いた", tags=("island", "cat"))
        self.add("t2", "汀へ種籾を渡した", tags=("seed", "handoff"), related=("t1",))
        candidates = self.store.recall(context="島へ戻る", tags=("island",), related_trace_ids=("t1",),
                                      limit=2, associative_slots=1, non_goal_slots=0)
        self.assertTrue(any(c.trace_id == "t2" and c.route == "associative" for c in candidates))

    def test_recall_candidate_is_logged(self):
        self.add("t1", "猫で島を歩いた", tags=("island",))
        candidates = self.store.recall(context="島", tags=("island",), limit=1,
                                      associative_slots=0, non_goal_slots=0)
        self.assertEqual(len(self.store.recall_events()), 1)
        self.assertEqual(self.store.recall_events()[0].recall_id, candidates[0].recall_id)

    def test_outcome_is_appended_without_overwriting_candidate(self):
        self.add("t1", "猫で島を歩いた", tags=("island",))
        candidate = self.store.recall(context="島", tags=("island",), limit=1,
                                      associative_slots=0, non_goal_slots=0)[0]
        self.store.record_outcome(candidate.recall_id, adopted=True,
                                  interpretation_changed=True, action_changed=False)
        rows = [r for r in self.store.recall_events() if r.recall_id == candidate.recall_id]
        self.assertEqual([r.status for r in rows], ["candidate", "outcome"])
        self.assertIsNone(rows[0].adopted)
        self.assertTrue(rows[1].interpretation_changed)

    def test_startup_view_does_not_replace_raw_trace(self):
        self.add("t1", "猫で島を歩いた", tags=("island",))
        self.store.add_memory(memory_id="m1", summary="島の記憶", source_trace_ids=("t1",))
        view = self.store.startup_view()
        self.assertEqual(view["current_memories"][0]["summary"], "島の記憶")
        self.assertEqual(view["unintegrated_trace_ids"], [])
        self.assertEqual(len(self.store.traces()), 1)

    def test_jsonl_is_human_readable_and_has_separate_layers(self):
        self.add("t1", "止まると、聞こえてくる", tags=("island", "listening"))
        self.store.add_memory(memory_id="m1", summary="停止と知覚", source_trace_ids=("t1",))
        files = {p.name for p in Path(self.tempdir.name).iterdir()}
        self.assertTrue({"traces.jsonl", "memory_revisions.jsonl"}.issubset(files))
        row = json.loads(self.store.trace_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(row["trace_id"], "t1")


if __name__ == "__main__":
    unittest.main()
