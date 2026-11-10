"""
EquiLogic AI & Global Turf Intelligence — 9-Rule Conditional Horse Racing Engine
Supports Class 1 through Class 6 Specialist Regimes, Tactical Pace Mapping,
100%-Normalized Win Probabilities, and Market Value Edge Detection.
"""

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RunnerInput:
    number: int
    name: str
    draw: int
    age: int
    weight_lbs: int          # e.g., 133 for 9-7, or kg converted to lbs
    weight_display: str      # e.g., "9-7" or "54.5kg"
    jockey: str
    jockey_claim_lbs: int    # e.g., 0, 3, 5, 7
    trainer: str
    official_rating: int     # OR
    form: str                # e.g., "213", "014", "003"
    career_runs: int
    is_second_hcap_start: bool
    days_since_last_run: int
    last_distance_furlongs: float
    course_winner: bool      # C
    distance_winner: bool    # D
    cd_winner: bool          # CD
    going_proven: bool
    headgear: str            # e.g., "", "b1", "p1", "t1", "v", "h1"
    is_class_dropper: bool
    carried_penalty_lbs: int
    running_style: str       # "Front-Runner", "Prominent", "Midfield", "Hold-Up"
    last_run_comment: str
    decimal_odds: float      # e.g., 2.50 for 6/4


@dataclass
class RaceInput:
    race_id: str
    date: str
    country: str
    track: str
    race_time: str
    race_name: str
    race_class: int          # 1 to 6
    race_type: str           # "Flat", "AW", "Hurdle", "Chase"
    distance_furlongs: float # 1 mile = 8.0 furlongs
    going: str
    source_url: str
    runners: List[RunnerInput]


@dataclass
class RunnerEvaluation:
    number: int
    name: str
    draw: int
    jockey: str
    trainer: str
    weight_display: str
    official_rating: int
    form: str
    decimal_odds: float
    raw_score: float
    win_probability: float
    top3_probability: float
    market_probability: float
    value_edge: float
    confidence_tier: str
    running_style: str
    green_flags: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    rule_breakdown: Dict[str, float] = field(default_factory=dict)


def detect_race_class(race_name: str, explicit_class: Optional[int] = None) -> int:
    """Auto-detects Race Class (1-6) from race title or explicit setting."""
    if explicit_class in (1, 2, 3, 4, 5, 6):
        return explicit_class
    text = race_name.upper()
    for c in range(1, 7):
        if f"CLASS {c}" in text or f"(C{c})" in text or f"CL{c}" in text:
            return c
    if any(k in text for k in ["GROUP 1", "GRADE 1", "GROUP 2", "GRADE 2", "GROUP 3", "GRADE 3", "LISTED"]):
        return 1
    if any(k in text for k in ["CLASSIFIED", "0-55", "0-60", "CLAIMING"]):
        return 6
    if any(k in text for k in ["0-70", "0-75", "NURSERY", "APPRENTICE", "CONDITIONAL"]):
        return 5
    return 4


def evaluate_race(race: RaceInput) -> Dict[str, Any]:
    """
    Evaluates all declared runners using the 9-Rule EquiLogic AI Engine:
      Rule 1: Recent Form (Last 3-5 Runs, 3/3 Podium Streak, Multi-Zero Slump vs Single-0 Bounce-Back)
      Rule 2: Course & Distance (C / D / CD)
      Rule 3: Going Suitability
      Rule 4: Days Since Last Run (DSLR Fitness Window & Class 5/6 Quick-Backup Penalty-King)
      Rule 5: Weight & Official Rating (OR)
      Rule 6: Headgear & First-Time Equipment (h1, b1, v1, p1, t1)
      Rule 7: Draw Bias (Course & Distance Calibrated)
      Rule 8: Furlong Distance Transition (1m = 8f, +-1.0f Tactical NLP Check)
      Rule 9: Race Class 1-6 Specialist Regime (9A Unexposed Improver, 9B Class-Dropper, 9C Claims & OR Ceiling)
    """
    r_class = detect_race_class(race.race_name, race.race_class)
    is_low_grade = r_class in (5, 6)
    max_or = max((r.official_rating for r in race.runners), default=0)
    min_weight = min((r.weight_lbs - r.jockey_claim_lbs for r in race.runners), default=126)

    evals: List[RunnerEvaluation] = []

    for r in race.runners:
        score = 50.0  # Unclamped baseline score
        greens: List[str] = []
        reds: List[str] = []
        breakdown: Dict[str, float] = {}

        clean_form = re.sub(r"[^0-9FUP]", "", r.form.upper())
        last3 = clean_form[-3:] if len(clean_form) >= 3 else clean_form
        last_char = clean_form[-1] if clean_form else ""

        # =====================================================================
        # RULE 1: RECENT FORM & BOUNCE-BACK LOGIC
        # =====================================================================
        r1_pts = 0.0
        if last_char == "1":
            r1_pts += 18.0
            greens.append(f"Rule 1: Last-time-out Winner (form '{r.form}', +18 pts)")
        elif last_char == "2":
            r1_pts += 12.0
            greens.append(f"Rule 1: Runner-up last time out (form '{r.form}', +12 pts)")
        elif last_char == "3":
            r1_pts += 8.0
            greens.append(f"Rule 1: Placed 3rd last time out (form '{r.form}', +8 pts)")
        elif last_char in ("F", "U", "P"):
            r1_pts -= 16.0
            reds.append(f"Rule 1: Failed to complete last run ('{last_char}', -16 pts)")

        # 3-for-3 podium consistency check
        if len(last3) == 3 and all(c in ("1", "2", "3") for c in last3):
            r1_pts += 16.0
            greens.append(f"Rule 1: 3-for-3 Podium Consistency Streak ('{last3}', +16 pts)")

        # Zero ('0') handling: Multi-zero slump vs Single-'0' bounce-back
        zeros_in_last3 = sum(1 for c in last3 if c in ("0", "P", "F", "U"))
        if zeros_in_last3 >= 2:
            r1_pts -= 24.0
            reds.append(f"Rule 1: Multi-zero recent slump ('{last3}', -24 pts)")
        elif zeros_in_last3 == 1:
            if is_low_grade and (last_char in ("1", "2", "3", "4") or r.is_class_dropper):
                r1_pts -= 2.0
                greens.append("Rule 1/9B: Single '0' forgiven due to bounce-back / class drop (-2 pts only)")
            else:
                r1_pts -= 14.0
                reds.append(f"Rule 1: Unplaced '0' in recent form ('{last3}', -14 pts)")
        breakdown["Rule 1 (Form)"] = r1_pts
        score += r1_pts

        # =====================================================================
        # RULE 2: COURSE & DISTANCE (C / D / CD)
        # =====================================================================
        r2_pts = 0.0
        if r.cd_winner:
            r2_pts += 20.0
            greens.append("Rule 2: Proven Course & Distance (CD) Winner (+20 pts)")
        elif r.course_winner and r.distance_winner:
            r2_pts += 16.0
            greens.append("Rule 2: Proven Course (C) and Distance (D) Winner (+16 pts)")
        elif r.course_winner:
            r2_pts += 10.0
            greens.append("Rule 2: Course Winner (C) (+10 pts)")
        elif r.distance_winner:
            r2_pts += 10.0
            greens.append("Rule 2: Distance Winner (D) (+10 pts)")
        else:
            if is_low_grade and (r.career_runs <= 4 or r.is_second_hcap_start):
                greens.append("Rule 2/9A: Exempt from unproven CD deduction (Unexposed Improver)")
            else:
                r2_pts -= 4.0
                reds.append("Rule 2: Unproven over Course & Distance (-4 pts)")
        breakdown["Rule 2 (C/D)"] = r2_pts
        score += r2_pts

        # =====================================================================
        # RULE 3: GOING SUITABILITY
        # =====================================================================
        r3_pts = 0.0
        if r.going_proven:
            r3_pts += 12.0
            greens.append(f"Rule 3: Proven on today's '{race.going}' going (+12 pts)")
        else:
            r3_pts -= 5.0
            reds.append(f"Rule 3: Unproven on '{race.going}' surface (-5 pts)")
        breakdown["Rule 3 (Going)"] = r3_pts
        score += r3_pts

        # =====================================================================
        # RULE 4: DAYS SINCE LAST RUN (DSLR) & QUICK-BACKUP PENALTY-KING
        # =====================================================================
        r4_pts = 0.0
        is_penalty_king = is_low_grade and last_char == "1" and 1 <= r.days_since_last_run <= 10
        if is_penalty_king:
            bonus = 34.0 if r.days_since_last_run <= 5 else 26.0
            r4_pts += bonus
            greens.append(
                f"Rule 4/9: Class {r_class} 'Penalty-King' Quick Turnaround ({r.days_since_last_run}d since win, +{int(bonus)} pts)"
            )
        elif 7 <= r.days_since_last_run <= 35:
            r4_pts += 10.0
            greens.append(f"Rule 4: Optimal fitness window ({r.days_since_last_run} days since last run, +10 pts)")
        elif 1 <= r.days_since_last_run < 7:
            r4_pts -= 8.0
            reds.append(f"Rule 4: Quick backup ({r.days_since_last_run} days) without last-start win (-8 pts)")
        elif 36 <= r.days_since_last_run <= 60:
            r4_pts += 2.0
        elif 61 <= r.days_since_last_run <= 150:
            r4_pts -= 8.0
            reds.append(f"Rule 4: Fitness check required ({r.days_since_last_run}d absence, -8 pts)")
        else:
            r4_pts -= 15.0
            reds.append(f"Rule 4: Long layoff ({r.days_since_last_run}d > 150d, -15 pts)")
        breakdown["Rule 4 (DSLR)"] = r4_pts
        score += r4_pts

        # =====================================================================
        # RULE 5: WEIGHT & OFFICIAL RATING (OR)
        # =====================================================================
        r5_pts = 0.0
        net_weight = r.weight_lbs - r.jockey_claim_lbs
        if r.carried_penalty_lbs > 0 and not is_penalty_king:
            r5_pts -= 6.0
            reds.append(f"Rule 5: Carries +{r.carried_penalty_lbs}lb penalty (-6 pts)")
        if net_weight <= min_weight + 3:
            r5_pts += 8.0
            greens.append(f"Rule 5: Featherweight / bottom-weight advantage ({r.weight_display}, +8 pts)")
        breakdown["Rule 5 (Weight/OR)"] = r5_pts
        score += r5_pts

        # =====================================================================
        # RULE 6: HEADGEAR & FIRST-TIME EQUIPMENT (h1, b1, v1, p1, t1)
        # =====================================================================
        r6_pts = 0.0
        hg = r.headgear.lower().strip()
        if any(code in hg for code in ("h1", "b1", "v1", "p1", "t1")):
            r6_pts += 14.0
            greens.append(f"Rule 6: First-Time Headgear catalyst ('{r.headgear}', +14 pts)")
        elif hg:
            r6_pts += 4.0
            greens.append(f"Rule 6: Retained headgear ('{r.headgear}', +4 pts)")
        breakdown["Rule 6 (Headgear)"] = r6_pts
        score += r6_pts

        # =====================================================================
        # RULE 7: DRAW BIAS (COURSE & DISTANCE CALIBRATED)
        # =====================================================================
        r7_pts = 0.0
        if race.race_type in ("Flat", "AW") and r.draw > 0:
            if race.distance_furlongs <= 7.5:
                if r.draw <= 4:
                    r7_pts += 12.0
                    greens.append(f"Rule 7: Prime inside sprint draw (Stall {r.draw} over {race.distance_furlongs}f, +12 pts)")
                elif r.draw >= 8:
                    r7_pts -= 10.0
                    reds.append(f"Rule 7: Wide sprint draw disadvantage (Stall {r.draw}, -10 pts)")
            elif race.distance_furlongs >= 9.5:
                if r.draw >= 8:
                    r7_pts -= 2.5  # Relaxed by 75% on middle-distance trips >= 9.5f
                elif r.draw <= 4:
                    r7_pts += 5.0
        breakdown["Rule 7 (Draw)"] = r7_pts
        score += r7_pts

        # =====================================================================
        # RULE 8: FURLONG DISTANCE TRANSITION (1m = 8f, +-1.0f TACTICAL CHECK)
        # =====================================================================
        r8_pts = 0.0
        diff_f = round(race.distance_furlongs - r.last_distance_furlongs, 2)
        comment_lower = r.last_run_comment.lower()

        if abs(diff_f) <= 0.5:
            if last_char in ("1", "2", "3"):
                r8_pts += 10.0
                greens.append(f"Rule 8: Proven at same trip ({race.distance_furlongs}f) with top-3 finish (+10 pts)")
        elif diff_f >= 1.0:
            # Stepping up in trip
            if any(k in comment_lower for k in ("ran on", "running on", "stayed on", "finishing well", "strong finish")):
                r8_pts += 16.0
                greens.append(f"Rule 8: Tactical step up (+{diff_f}f) backed by 'running on/stayed on' comment (+16 pts)")
            elif r.distance_winner:
                r8_pts += 8.0
                greens.append(f"Rule 8: Stepping up (+{diff_f}f) to a proven winning trip (+8 pts)")
            else:
                r8_pts -= 10.0
                reds.append(f"Rule 8: Unproven Stamina Risk stepping up +{diff_f}f (-10 pts)")
        elif diff_f <= -1.0:
            # Dropping back in trip
            if any(k in comment_lower for k in ("weakened", "faded", "tired", "headed late", "no extra")):
                r8_pts += 19.0
                greens.append(f"Rule 8: Positive trainer drop in trip ({diff_f}f) after fading/weakening late (+19 pts)")
            elif r.distance_winner:
                r8_pts += 8.0
                greens.append(f"Rule 8: Dropping back ({diff_f}f) to proven distance (+8 pts)")
            else:
                r8_pts -= 8.0
                reds.append(f"Rule 8: Early Pace Risk dropping back {diff_f}f without sprint proof (-8 pts)")
        breakdown["Rule 8 (Distance Transition)"] = r8_pts
        score += r8_pts

        # =====================================================================
        # RULE 9: RACE CLASS 1-6 SPECIALIST REGIME LOGIC
        # =====================================================================
        r9_pts = 0.0
        if is_low_grade:
            # Rule 9A: Unexposed 2nd-Start Handicap / Lightly-Raced Improver
            if r.career_runs <= 4 or r.is_second_hcap_start:
                r9_pts += 24.0
                greens.append(f"Rule 9A: Unexposed Class {r_class} Improver ({r.career_runs} starts / 2nd Hcap, +24 pts)")
            # Rule 9B: Class-Dropper Relief ("back in calmer waters")
            if r.is_class_dropper or "calmer waters" in comment_lower or "dropped in class" in comment_lower:
                r9_pts += 18.0
                greens.append(f"Rule 9B: Class-Dropper into Class {r_class} calmer waters (+18 pts)")
            # Rule 9C: Apprentice Weight Claims (3)/(5)/(7) & Class-Ceiling Top-Weight OR
            if r.jockey_claim_lbs >= 5:
                r9_pts += 12.0
                greens.append(f"Rule 9C: Valuable {r.jockey_claim_lbs}lb apprentice jockey claim in Class {r_class} (+12 pts)")
            elif r.jockey_claim_lbs >= 3:
                r9_pts += 6.0
                greens.append(f"Rule 9C: Useful {r.jockey_claim_lbs}lb rider claim in Class {r_class} (+6 pts)")
            if max_or > 0 and r.official_rating >= max_or - 1:
                r9_pts += 10.0
                greens.append(f"Rule 9C: Class-Ceiling OR Leader (OR {r.official_rating}) in Class {r_class} (+10 pts)")
        else:
            # Class 1-4: High OR + clean profile premium
            if max_or > 0 and r.official_rating >= max_or:
                r9_pts += 8.0
                greens.append(f"Rule 9: Top-rated contender (OR {r.official_rating}) in Class {r_class} (+8 pts)")
            if r.is_class_dropper:
                r9_pts += 10.0
                greens.append(f"Rule 9: Dropping in grade into Class {r_class} (+10 pts)")

        breakdown["Rule 9 (Class Regime)"] = r9_pts
        score += r9_pts

        market_prob = (1.0 / r.decimal_odds) * 100.0 if r.decimal_odds > 1.0 else 10.0

        evals.append(
            RunnerEvaluation(
                number=r.number,
                name=r.name,
                draw=r.draw,
                jockey=r.jockey,
                trainer=r.trainer,
                weight_display=r.weight_display,
                official_rating=r.official_rating,
                form=r.form,
                decimal_odds=r.decimal_odds,
                raw_score=round(score, 2),
                win_probability=0.0,
                top3_probability=0.0,
                market_probability=round(market_prob, 2),
                value_edge=0.0,
                confidence_tier="Medium",
                running_style=r.running_style,
                green_flags=greens,
                red_flags=reds,
                rule_breakdown=breakdown,
            )
        )

    # Normalize probabilities across the field to sum to exactly 100.00%
    # Softmax temperature calibrated for unclamped multi-factor scores
    max_s = max((e.raw_score for e in evals), default=50.0)
    exp_weights = [math.exp((e.raw_score - max_s) / 18.0) for e in evals]
    total_exp = sum(exp_weights) or 1.0

    for e, w in zip(evals, exp_weights):
        win_p = (w / total_exp) * 100.0
        e.win_probability = round(win_p, 2)
        e.top3_probability = round(min(95.0, win_p * 2.35), 2)
        e.value_edge = round(e.win_probability - e.market_probability, 2)
        if e.win_probability >= 32.0 or e.raw_score >= 115.0:
            e.confidence_tier = "High"
        elif e.win_probability >= 18.0 or e.raw_score >= 85.0:
            e.confidence_tier = "Medium"
        else:
            e.confidence_tier = "Low"

    # Sort descending by raw_score (and win_probability)
    evals.sort(key=lambda x: (x.raw_score, x.win_probability), reverse=True)

    # Fix rounding drift so win_probability sums to 100.00%
    if evals:
        drift = round(100.0 - sum(e.win_probability for e in evals), 2)
        evals[0].win_probability = round(evals[0].win_probability + drift, 2)

    # Tactical Pace Map Summary
    front_runners = [e.name for e in evals if e.running_style in ("Front-Runner", "Prominent")]
    pace_tempo = "HIGH (Strong Pace — Favors Closers)" if len(front_runners) >= 3 else (
        "LOW (Tactical Crawl — Favors Front-Runners)" if len(front_runners) <= 1 else "MODERATE (True Run Race)"
    )

    podium = evals[:3]
    value_candidates = sorted(evals, key=lambda x: x.value_edge, reverse=True)
    best_value = value_candidates[0] if value_candidates else None

    return {
        "race_id": race.race_id,
        "date": race.date,
        "country": race.country,
        "track": race.track,
        "race_time": race.race_time,
        "race_name": race.race_name,
        "detected_class": r_class,
        "race_type": race.race_type,
        "distance_furlongs": race.distance_furlongs,
        "going": race.going,
        "source_url": race.source_url,
        "pace_tempo": pace_tempo,
        "likely_leaders": front_runners[:2] if front_runners else [evals[0].name],
        "predicted_winner": evals[0].name if evals else "N/A",
        "winner_probability": evals[0].win_probability if evals else 0.0,
        "winner_score": evals[0].raw_score if evals else 0.0,
        "podium": [
            {"rank": idx + 1, "name": p.name, "score": p.raw_score, "win_prob": p.win_probability, "odds": p.decimal_odds}
            for idx, p in enumerate(podium)
        ],
        "best_value_candidate": {
            "name": best_value.name,
            "win_prob": best_value.win_probability,
            "market_prob": best_value.market_probability,
            "value_edge": best_value.value_edge,
            "odds": best_value.decimal_odds,
        } if best_value else None,
        "runners": [
            {
                "rank": idx + 1,
                "number": e.number,
                "name": e.name,
                "draw": e.draw,
                "jockey": e.jockey,
                "trainer": e.trainer,
                "weight": e.weight_display,
                "or": e.official_rating,
                "form": e.form,
                "decimal_odds": e.decimal_odds,
                "raw_score": e.raw_score,
                "win_probability": e.win_probability,
                "top3_probability": e.top3_probability,
                "market_probability": e.market_probability,
                "value_edge": e.value_edge,
                "confidence_tier": e.confidence_tier,
                "running_style": e.running_style,
                "green_flags": e.green_flags,
                "red_flags": e.red_flags,
                "rule_breakdown": e.rule_breakdown,
            }
            for idx, e in enumerate(evals)
        ],
    }
