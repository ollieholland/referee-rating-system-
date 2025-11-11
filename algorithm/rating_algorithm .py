"""
rating_algorithm.py
Computes referee match rating (decimal) and integrates Match Difficulty Rating (MDR).
"""

import pandas as pd
from typing import Dict
from math import isfinite

# Import MDR
from algorithm.match_difficulty import compute_match_difficulty

# Default component weights for base performance (these operate on 0-10 subscores)
COMPONENT_WEIGHTS = {
    "decision_accuracy": 0.40,
    "foul_management": 0.30,
    "var_handling": 0.15,
    "game_flow": 0.15
}

def clamp_rating(x: float, lo: float = 1.0, hi: float = 10.0) -> float:
    if not isfinite(x):
        return lo
    return round(max(lo, min(hi, x)), 2)

def compute_base_rating_from_subscores(decision_accuracy: float, foul_management: float, var_handling: float, game_flow: float, weights: Dict = None) -> float:
    """
    Each subscore is expected in 0..10 range. Returns base rating in 0..10.
    """
    w = COMPONENT_WEIGHTS if weights is None else {**COMPONENT_WEIGHTS, **weights}
    base = (
        decision_accuracy * w['decision_accuracy'] +
        foul_management * w['foul_management'] +
        var_handling * w['var_handling'] +
        game_flow * w['game_flow']
    )
    # base is already scaled to 0..10
    return round(base, 2)

def compute_final_rating(match_row: Dict, mdr_weights: Dict = None, min_multiplier: float = 0.8, max_multiplier: float = 1.8) -> Dict:
    """
    Given a match_row (dict or pandas Series) containing the needed performance subscores
    and the match-context fields required by compute_match_difficulty, calculates:
      - base_rating
      - mdr_multiplier
      - final_rating_clamped (1..10)
    Returns a dict with all three.
    Expected fields in match_row for subscores:
      - decision_accuracy (0..10)
      - foul_management (0..10)
      - var_handling (0..10)
      - game_flow (0..10)
    Plus fields used by match_difficulty module (see that module docstring).
    """
    # Read subscores safely
    get = lambda k, default=0.0: float(match_row.get(k, default)) if isinstance(match_row, dict) else float(getattr(match_row, k, default))
    da = get('decision_accuracy', 5.0)
    fm = get('foul_management', 5.0)
    vh = get('var_handling', 5.0)
    gf = get('game_flow', 5.0)

    base_rating = compute_base_rating_from_subscores(da, fm, vh, gf)
    # Compute MDR multiplier from match context
    mdr_inputs = match_row  # match_row is dict-like and should contain the needed keys
    mdr = compute_match_difficulty(mdr_inputs, weights=mdr_weights, min_multiplier=min_multiplier, max_multiplier=max_multiplier)

    # Apply multiplier. To keep final score within 1..10, we renormalize:
    # Approach: scaled = base_rating * mdr; then if >10 cap to 10, if <1 set to 1
    adjusted = base_rating * mdr

    # Optionally, if adjusted > 10, scale down keeping proportion to base (but we prefer clamping)
    final = clamp_rating(adjusted, lo=1.0, hi=10.0)

    return {
        'base_rating': round(base_rating, 2),
        'mdr_multiplier': mdr,
        'final_rating': final
    }

# Example convenience function to run on a dataframe
def rate_dataframe(df: pd.DataFrame, mdr_weights: Dict = None,
                   min_multiplier: float = 0.8, max_multiplier: float = 1.8) -> pd.DataFrame:
    """
    Expects df to contain columns: decision_accuracy, foul_management, var_handling, game_flow
    and match-context columns required by match_difficulty.
    Returns df with new columns: base_rating, mdr_multiplier, final_rating
    """
    rows_out = []
    for _, row in df.iterrows():
        info = compute_final_rating(row.to_dict(), mdr_weights=mdr_weights, min_multiplier=min_multiplier, max_multiplier=max_multiplier)
        rows_out.append(info)
    out = df.copy()
    out['base_rating'] = [r['base_rating'] for r in rows_out]
    out['mdr_multiplier'] = [r['mdr_multiplier'] for r in rows_out]
    out['final_rating'] = [r['final_rating'] for r in rows_out]
    return out
