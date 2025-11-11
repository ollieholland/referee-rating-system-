# algorithm/match_difficulty.py
"""
Match Difficulty Rating (MDR) Module
------------------------------------
Calculates a match difficulty multiplier based on contextual factors
such as rivalry, attendance, importance, weather, and team behaviour.
This helps adjust referee performance scores for fairness.
"""

def compute_match_difficulty(match_data):
    """
    Computes a Match Difficulty Rating (MDR) for a given match.

    match_data = {
        "importance": 0–1,        # Match importance (title/relegation implications)
        "rivalry": 0–1,           # Rivalry intensity
        "attendance": 0–1,        # Percentage of stadium filled
        "fouls": 0–1,             # Expected foul frequency
        "var": 0–1,               # VAR incident likelihood
        "dissent": 0–1,           # Dissent tendency of teams
        "weather": 0–1,           # Weather severity
        "fixture_history": 0–1    # Historical card tension in fixture
    }
    """

    # --- Fixed Weights (can be tuned later) ---
    weights = {
        'importance': 0.30,
        'rivalry': 0.25,
        'attendance': 0.15,
        'fouls': 0.10,
        'var': 0.10,
        'dissent': 0.05,
        'weather': 0.03,
        'fixture_history': 0.02
    }

    # --- Weighted sum of all components ---
    mdr_score = sum(match_data[key] * weights[key] for key in weights)

    # --- Scale to multiplier (1.0 = normal, up to 1.8 = very difficult) ---
    mdr_multiplier = 1.0 + (mdr_score * 0.8)

    return {
        "mdr_score": round(mdr_score, 3),
        "mdr_multiplier": round(mdr_multiplier, 3)
    }

