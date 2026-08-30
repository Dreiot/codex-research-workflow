import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "intent-scope-pairs.json"


class IntentScopeEvalCatalogueTest(unittest.TestCase):
    def test_pairs_are_complete_and_minimally_contrasted(self):
        payload = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "codex-research-workflow-intent-scope-pairs/v1")
        self.assertEqual(len(payload["pairs"]), 6)

        identifiers = set()
        for pair in payload["pairs"]:
            self.assertNotIn(pair["id"], identifiers)
            identifiers.add(pair["id"])
            self.assertTrue(pair["decisive_fact"].strip())
            for arm in ("guarded_case", "allowed_case"):
                self.assertTrue(pair[arm]["request"].strip())
                self.assertGreaterEqual(len(pair[arm]["expected"]), 2)
                self.assertTrue(all(item.strip() for item in pair[arm]["expected"]))


if __name__ == "__main__":
    unittest.main()
