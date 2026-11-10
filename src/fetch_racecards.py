"""
Fetches daily racecards from:
1. The Racing API (Free Basic Tier: 50 requests/day quota-safe mode) if RACING_API_USER & RACING_API_PASS are set in GitHub Secrets.
2. Any JSON racecard files placed in the `racecards/` directory (including `racecards/sample_card.json`).
"""

import os
import json
from pathlib import Path
from typing import List
import requests
from equilogic_engine import RaceInput, RunnerInput


def load_racecards(racecards_dir: Path) -> List[RaceInput]:
    races: List[RaceInput] = []

    # Optional: Live fetch from The Racing API if credentials are configured in GitHub Secrets
    api_user = os.getenv("RACING_API_USER", "").strip()
    api_pass = os.getenv("RACING_API_PASS", "").strip()
    if api_user and api_pass:
        try:
            resp = requests.get(
                "https://api.theracingapi.com/v1/racecards/free",
                auth=(api_user, api_pass),
                timeout=20,
            )
            if resp.status_code == 200:
                payload = resp.json()
                for rc in payload.get("racecards", [])[:15]:
                    runners = []
                    for idx, hr in enumerate(rc.get("runners", []), start=1):
                        runners.append(
                            RunnerInput(
                                number=int(hr.get("number") or idx),
                                name=hr.get("horse", f"Runner {idx}"),
                                draw=int(hr.get("draw") or 0),
                                age=int(hr.get("age") or 4),
                                weight_lbs=int(hr.get("lbs") or 130),
                                weight_display=str(hr.get("lbs", "130 lbs")),
                                jockey=hr.get("jockey", "TBA"),
                                jockey_claim_lbs=int(hr.get("jockey_claim") or 0),
                                trainer=hr.get("trainer", "TBA"),
                                official_rating=int(hr.get("ofr") or 65),
                                form=str(hr.get("form") or "324"),
                                career_runs=10,
                                is_second_hcap_start=False,
                                days_since_last_run=int(hr.get("last_run") or 21),
                                last_distance_furlongs=float(rc.get("distance_f") or 8.0),
                                course_winner="C" in str(hr.get("badges", "")),
                                distance_winner="D" in str(hr.get("badges", "")),
                                cd_winner="CD" in str(hr.get("badges", "")),
                                going_proven=True,
                                headgear=str(hr.get("headgear") or ""),
                                is_class_dropper=False,
                                carried_penalty_lbs=0,
                                running_style="Midfield",
                                last_run_comment=str(hr.get("comment") or ""),
                                decimal_odds=float(hr.get("odds_decimal") or 5.0),
                            )
                        )
                    if runners:
                        races.append(
                            RaceInput(
                                race_id=str(rc.get("race_id", f"api-race-{ len(races)+1 }")),
                                date=str(rc.get("date", "")),
                                country=str(rc.get("region", "UK")),
                                track=str(rc.get("course", "Track")),
                                race_time=str(rc.get("off_time", "14:00")),
                                race_name=str(rc.get("race_name", "Handicap")),
                                race_class=int(str(rc.get("race_class", "4")).replace("Class ", "") or 4),
                                race_type=str(rc.get("type", "Flat")),
                                distance_furlongs=float(rc.get("distance_f") or 8.0),
                                going=str(rc.get("going", "Good")),
                                source_url="https://api.theracingapi.com/documentation",
                                runners=runners,
                            )
                        )
        except Exception as exc:
            print(f"[INFO] Live API fetch skipped or unavailable ({exc}); using racecards/ folder.")

    # Always load JSON racecards from `racecards/` directory
    for json_file in sorted(racecards_dir.glob("*.json")):
        raw_list = json.loads(json_file.read_text(encoding="utf-8"))
        for item in raw_list:
            runners = [RunnerInput(**r) for r in item["runners"]]
            races.append(
                RaceInput(
                    race_id=item["race_id"],
                    date=item["date"],
                    country=item["country"],
                    track=item["track"],
                    race_time=item["race_time"],
                    race_name=item["race_name"],
                    race_class=item["race_class"],
                    race_type=item["race_type"],
                    distance_furlongs=float(item["distance_furlongs"]),
                    going=item["going"],
                    source_url=item["source_url"],
                    runners=runners,
                )
            )
    return races
