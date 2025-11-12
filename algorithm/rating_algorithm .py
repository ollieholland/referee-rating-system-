"""
rating_algorithm.py
-------------------
This module computes referee ratings using:
1. Match Difficulty Score (MDS)
2. Dual-Mode difficulty weighting (easy / medium / hard)
3. Final referee rating (1–10 scale, with smart safeguards)

Upcoming additions:
- Consistency Rating (past 5 matches)
- Error Severity Index (ESI) for weighted decision impact
"""

import numpy as np
import pandas as pd

# ============================================================
# 1. MATCH DIFFICULTY SCORE (MDS)
# ============================================================

def compute_match_difficulty(row):
    """
    Creates a 0–1 difficulty score for each match.
    Higher = more challenging environment for the referee.
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

    score = sum(row[f] * w for f, w in weights.items())
    return max(0.0, min(1.0, score))


# ============================================================
# 2. DIFFICULTY CATEGORY (EASY / MEDIUM / HARD)
# ============================================================

def difficulty_category(mds):
    """
    Assigns difficulty label based on the match difficulty score.
    """
    if mds < 0.45:
        return "easy"
    elif mds > 0.55:
        return "hard"
    else:
        return "medium"


# ============================================================
# 3. WEIGHT SETS FOR DUAL-MODE SCORING
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
# 4. FINAL RATING FUNCTION (with safeguarding for easy matches)
# ============================================================

def compute_final_rating(row):
    """
    Computes the final referee rating using dual-mode weighting.
    Includes:
    - Match difficulty calculation
    - Difficulty mode selection
    - Weighted performance score
    - Minimum baseline score protection for 'easy' matches
    """

    # ---- Difficulty calculations ----
    mds = compute_match_difficulty(row)
    mode = difficulty_category(mds)
    w = WEIGHTS[mode]

    # ---- Weighted performance score ----
    raw_rating = sum(row[f] * w[f] * 10 for f in w)  # scaled to 1–10 range

    # ---- Prevent unfairly low scores in easy games ----
    if mode == "easy":
        raw_rating = max(raw_rating, 6.5)

    # Return structured result
    return {
        "mds": round(mds, 3),
        "difficulty_mode": mode,
        "final_rating": round(raw_rating, 2)
    }


# ============================================================
# 5. APPLY ALGORITHM TO AN ENTIRE DATAFRAME
# ============================================================

def rate_dataframe(df):
    """
    Takes a referee dataset and adds:
    - match difficulty score
    - difficulty mode
    - final rating
    """
    results = df.apply(lambda row: compute_final_rating(row), axis=1, result_type='expand')
    df["mds"] = results["mds"]
    df["difficulty_mode"] = results["difficulty_mode"]
    df["final_rating"] = results["final_rating"]
    return df


# ============================================================
# 6. PLACEHOLDERS FOR FUTURE FEATURES (to be implemented next)
# ============================================================

def compute_consistency_rating():
    """
    TODO (Oliver + ChatGPT Step D):
    Based on last 5 matches:
    - Reward consistent performance
    - Penalize volatility
    """
    pass


def compute_error_severity_index():
    """
    TODO (Oliver + ChatGPT Step E):
    Weighted classification of:
    - Minor Errors
    - Moderate Errors
    - Major Errors
    - Critical Errors
    """
    pass


# End of rating_algorithm.py


