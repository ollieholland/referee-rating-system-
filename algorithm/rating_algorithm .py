"""
rating_algorithm.py
-------------------
Full referee rating engine including:

1. Match Difficulty Score (MDS)
2. Dual-Mode Difficulty System (easy / medium / hard)
3. Final Match Rating (1–10 scale)
4. Error Severity Index (ESI) — minor / moderate / major errors
5. Consistency Rating — rolling volatility over last 5 matches
6. Form Rating — 5-game rolling average
7. Season Average Rating — per referee

Author: Oliver Holland
"""

import numpy as np
import pandas as pd

# ============================================================
# 1. MATCH DIFFICULTY SCORE (MDS)
# ============================================================

def compute_match_difficulty(row):
    """
    Produces a 0–1 score showing how hard a match was to referee.
    """

    weights = {
        'crowd_pressure': 0.20,
        'attendance_pct': 0.15,
        'rivalry_intensity': 0.20,
        'match_importance': 0.25,
        'var_overturns': 0.05,
        'foul_management': 0.05,
        'decision_accuracy': 0.10
    }

    score = sum(row.get(f, 0) * w for f, w in weights.items())
    return max(0.0, min(1.0, score))


# ============================================================
# 2. DIFFICULTY CATEGORY LABEL (EASY / MEDIUM / HARD)
# ============================================================

def difficulty_category(mds):
    if mds < 0.45:
        return "easy"
    elif mds > 0.55:
        return "hard"
    else:
        return "medium"


# ============================================================
# 3. WEIGHT SETS FOR FINAL MATCH RATING
# ============================================================

WEIGHTS = {
    "easy": {
        'decision_accuracy': 0.50,
        'foul_management': 0.20,
        'var_overturns': 0.05,
        'crowd_pressure': 0.05,
        'match_importance': 0.05,
        'attendance_pct': 0.05,
        'rivalry_intensity': 0.10
    },
    "medium": {
        'decision_accuracy': 0.35,
        'foul_management': 0.25,
        'var_overturns': 0.10,
        'crowd_pressure': 0.10,
        'match_importance': 0.10,
        'attendance_pct': 0.05,
        'rivalry_intensity': 0.05
    },
    "hard": {
        'decision_accuracy': 0.25,
        'foul_management': 0.25,
        'var_overturns': 0.15,
        'crowd_pressure': 0.15,
        'match_importance': 0.10,
        'attendance_pct': 0.05,
        'rivalry_intensity': 0.05
    }
}


# ============================================================
# 4. ERROR SEVERITY INDEX (ESI)
# ============================================================

def compute_error_severity_index(row):
    """
    Applies realistic penalties for referee mistakes.
    Negative values reduce the referee’s match rating.
    """

    weights = {
        "minor_errors": -0.05,
        "moderate_errors": -0.15,
        "major_errors": -0.40
    }

    penalty = (
        row.get("minor_errors", 0) * weights["minor_errors"] +
        row.get("moderate_errors", 0) * weights["moderate_errors"] +
        row.get("major_errors", 0) * weights["major_errors"]
    )

    return penalty


# ============================================================
# 5. FINAL MATCH RATING (CORE CALCULATION)
# ============================================================

def compute_final_rating(row, esi_penalty, consistency_bonus):
    """
    Produces a referee rating (1–10) using:

    - Dual-mode difficulty weighting
    - Error severity penalties
    - Consistency bonuses

    Includes fairness protection for easy matches.
    """

    mds = compute_match_difficulty(row)
    mode = difficulty_category(mds)
    w = WEIGHTS[mode]

    # Base performance rating
    base_rating = sum(row.get(f, 0) * w[f] * 10 for f in w)

    # Add penalties and bonuses
    final_rating = base_rating + esi_penalty + consistency_bonus

    # Fairness floor for easy matches
    if mode == "easy":
        final_rating = max(final_rating, 6.5)

    # Bound between 1 and 10
    final_rating = max(1.0, min(10.0, final_rating))

    return {
        "mds": round(mds, 3),
        "difficulty_mode": mode,
        "final_rating": round(final_rating, 2)
    }


# ============================================================
# 6. CONSISTENCY RATING (VOLATILITY OVER LAST 5 MATCHES)
# ============================================================

def compute_consistency_bonus(df):
    """
    Rewards referees who perform stably over 5 matches.

    Low volatility = bonus
    High volatility = penalty
    """

    bonuses = {}

    for referee in df['referee'].unique():
        ref_df = df[df['referee'] == referee].sort_values("match_id")

        rolling_std = ref_df['final_rating'].rolling(window=5).std()

        for i, std_val in enumerate(rolling_std):
            idx = ref_df.index[i]

            if i < 4:
                bonuses[idx] = 0
                continue

            if std_val < 0.15:
                bonuses[idx] = 0.20
            elif std_val < 0.30:
                bonuses[idx] = 0.10
            elif std_val < 0.50:
                bonuses[idx] = 0.00
            else:
                bonuses[idx] = -0.15

    return bonuses


# ============================================================
# 7. 5-GAME FORM + SEASON AVERAGE
# ============================================================

def compute_form_and_season_averages(df):
    form_dict = {}
    season_dict = {}

    for referee in df['referee'].unique():
        ref_matches = df[df['referee'] == referee].sort_values("match_id")

        # Season average
        season_avg = ref_matches["final_rating"].mean()
        season_dict[referee] = round(season_avg, 2)

        # Rolling 5-game form
        rolling_form = ref_matches["final_rating"].rolling(window=5).mean()

        for idx, val in zip(ref_matches.index, rolling_form):
            form_dict[idx] = round(val, 2) if not np.isnan(val) else None

    return form_dict, season_dict


# ============================================================
# 8. MAIN PIPELINE TO RATE A FULL DATAFRAME
# ============================================================

def rate_dataframe(df):
    """
    Runs the full referee rating model.

    Produces:
    - Match difficulty score
    - Difficulty mode
    - Final match rating
    - Consistency rating
    - 5-game form
    - Season average
    """

    # STEP 1 — Base ratings (without consistency bonus)
    base_results = []
    for _, row in df.iterrows():
        esi = compute_error_severity_index(row)
        result = compute_final_rating(row, esi_penalty=esi, consistency_bonus=0)
        base_results.append(result["final_rating"])

    df["final_rating"] = base_results

    # STEP 2 — Consistency bonus
    consistency_bonus = compute_consistency_bonus(df)

    # STEP 3 — Recalculate final results with consistency
    final_results = []
    for idx, row in df.iterrows():
        esi = compute_error_severity_index(row)
        bonus = consistency_bonus[idx]
        result = compute_final_rating(row, esi_penalty=esi, consistency_bonus=bonus)
        final_results.append(result)

    df["mds"] = [r["mds"] for r in final_results]
    df["difficulty_mode"] = [r["difficulty_mode"] for r in final_results]
    df["final_rating"] = [r["final_rating"] for r in final_results]

    # STEP 4 — 5-game form + season average
    form_dict, season_dict = compute_form_and_season_averages(df)

    df["form_5_games"] = df.index.map(form_dict)
    df["season_average"] = df["referee"].map(season_dict)

    return df
