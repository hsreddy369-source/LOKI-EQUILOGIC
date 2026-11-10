import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from equilogic_engine import evaluate_race
from fetch_racecards import load_racecards


class TestEquiLogic9Rules(unittest.TestCase):
    def test_all_9_rules_and_class_regimes(self):
        racecards_dir = Path(__file__).resolve().parent.parent / "racecards"
        races = load_racecards(racecards_dir)
        self.assertGreaterEqual(len(races), 4)

        by_id = {r.race_id: evaluate_race(r) for r in races}

        # 1. Verify Class 6 Penalty-King turnaround winner (Oppenheimer at Wolverhampton)
        w_c6 = by_id["wolves-1700-c6"]
        self.assertEqual(w_c6["detected_class"], 6)
        self.assertEqual(w_c6["predicted_winner"], "Oppenheimer")
        self.assertAlmostEqual(sum(r["win_probability"] for r in w_c6["runners"]), 100.0, places=1)

        # 2. Verify Class 5 Unexposed 2nd-Hcap + -1f Faded Drop winner (Astrid at Wolverhampton)
        w_c5 = by_id["wolves-2030-c5"]
        self.assertEqual(w_c5["detected_class"], 5)
        self.assertEqual(w_c5["predicted_winner"], "Astrid")

        # 3. Verify Hyderabad Malakpet Class 5 (Amboseli: CD + Stall 1 + 3lb claim + b1)
        hyd = by_id["hyderabad-malakpet-r1-c5"]
        self.assertEqual(hyd["detected_class"], 5)
        self.assertEqual(hyd["predicted_winner"], "Amboseli")

        # 4. Verify Class 1 Cheltenham Paddy Power Gold Cup (Meetmebythesea)
        chelt = by_id["cheltenham-1420-c1"]
        self.assertEqual(chelt["detected_class"], 1)
        self.assertEqual(chelt["predicted_winner"], "Meetmebythesea")


if __name__ == "__main__":
    unittest.main()
