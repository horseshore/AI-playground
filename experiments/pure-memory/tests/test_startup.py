import tempfile
import unittest

from startup import StartupError, start
from src.pure_memory import PureMemoryStore


SEED = """{"trace_id":"seed-1","event":"一回きりの出来事","source":"remote-seed","observations":["観察"],"inferences":["推論"],"tags":["one-off"],"one_off":true}
{"trace_id":"seed-2","event":"別の出来事","source":"remote-seed","tags":["other"]}
"""


class StartupTests(unittest.TestCase):
    def test_startup_merges_seed_and_returns_view(self):
        with tempfile.TemporaryDirectory() as root:
            result = start(root, seed_text=SEED)
            self.assertEqual(result["status"], "ready")
            self.assertEqual(result["sync"]["added"], 2)
            self.assertEqual(len(result["store"].traces()), 2)
            self.assertIn("seed-1", result["startup_view"]["unintegrated_trace_ids"])

    def test_restart_does_not_duplicate_seed(self):
        with tempfile.TemporaryDirectory() as root:
            first = start(root, seed_text=SEED)
            second = start(root, seed_text=SEED)
            self.assertEqual(first["sync"]["added"], 2)
            self.assertEqual(second["sync"]["added"], 0)
            self.assertEqual(second["sync"]["unchanged"], 2)
            self.assertEqual(len(second["store"].traces()), 2)

    def test_seed_id_conflict_fails_without_overwriting_original(self):
        with tempfile.TemporaryDirectory() as root:
            store = PureMemoryStore(root)
            store.record(trace_id="seed-1", event="元の記録", source="local")
            with self.assertRaises(StartupError):
                start(root, seed_text=SEED)
            self.assertEqual(store.traces()[0].event, "元の記録")

    def test_invalid_seed_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(StartupError):
                start(root, seed_text='{"trace_id":')
