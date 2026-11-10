"""
Main daily entrypoint executed by GitHub Actions 365 days a year.
Loads racecards, runs the 9-Rule EquiLogic AI engine, updates the immutable ledger in `data/`,
and publishes the daily report and GitHub Pages dashboard in `docs/`.
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from equilogic_engine import evaluate_race
from fetch_racecards import load_racecards
from notify import build_reports_and_notify

ROOT_DIR = Path(__file__).resolve().parent.parent
RACECARDS_DIR = ROOT_DIR / "racecards"
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    class_filter = os.getenv("RACE_CLASS_FILTER", "ALL").strip().upper()
    races = load_racecards(RACECARDS_DIR)

    evaluated_results = []
    for race in races:
        res = evaluate_race(race)
        if class_filter.startswith("CLASS "):
            target_c = int(class_filter.replace("CLASS ", "").strip())
            if res["detected_class"] != target_c:
                continue
        evaluated_results.append(res)

    # Save latest daily snapshot + append to immutable ledger
    now_iso = datetime.now(timezone.utc).isoformat()
    latest_path = DATA_DIR / "latest_predictions.json"
    latest_path.write_text(
        json.dumps({"generated_at_utc": now_iso, "races_analyzed": len(evaluated_results), "results": evaluated_results}, indent=2),
        encoding="utf-8",
    )

    history_path = DATA_DIR / "daily_predictions_history.json"
    history = []
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            history = []

    history.append({
        "run_timestamp_utc": now_iso,
        "races_count": len(evaluated_results),
        "winners_summary": [
            {
                "race_id": r["race_id"],
                "track": r["track"],
                "race_time": r["race_time"],
                "detected_class": r["detected_class"],
                "predicted_winner": r["predicted_winner"],
                "winner_probability": r["winner_probability"],
            }
            for r in evaluated_results
        ],
    })
    # Keep last 365 days (up to 730 twice-daily runs)
    history = history[-730:]
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    build_reports_and_notify(evaluated_results, DOCS_DIR)
    print(f"[SUCCESS] EquiLogic AI evaluated {len(evaluated_results)} races at {now_iso}.")


if __name__ == "__main__":
    main()
