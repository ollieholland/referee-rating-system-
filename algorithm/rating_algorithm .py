"""
Referee Rating Algorithm
------------------------
This module calculates a referee's performance rating for a given match,
taking into account factors such as correct decisions, VAR interventions,
foul management, and contextual match difficulty (MDR).

The algorithm is designed for transparency and modularity, allowing
football analysts and students to understand and extend the logic easily.
"""

from algorithm.match_difficulty import compute_match_difficulty


def compute_referee_rating(match_stats, match_context):
    """
    Calculates a referee's final rating for a given match.

    Parameters
    ----------
    match_stats : dict
        Referee performance metrics from the match:
        {
            "correct_decisions": int,
            "clear_errors": int,
            "var_overturns": int,
            "foul_management": float,   # quality of foul control (0–1)
            "time_in_play": float       # minutes ball was in play (out of 90)
        }

    match_context : dict
        Contextual difficulty factors for the match:
        {
            "importance": 0–1,
            "rivalry": 0–1,
            "attendance": 0–1,
            "fouls": 0–1,
            "var": 0–1,
            "dissent": 0–1,
            "weather": 0–1,
            "fixture_history": 0–1
        }

    Returns
    -------
    dict
        {
            "base_rating": float,
            "mdr_score": float,
            "mdr_multiplier": float,
            "final_rating": float
        }
    """

    # --- Weighting system for referee performance ---
    # Adjust these as your model becomes more data-driven.
    weights = {
        "correct_decisions": 0.35,
        "clear_errors": -0.25,
        "var_overturns": -0.10,
        "foul_management": 0.20,
        "time_in_play": 0.10
    }

    # --- Normalize and compute base rating (0–10 scale) ---
    base_score = (
        weights["correct_decisions"] * match_stats["correct_decisions"]
        + weights["clear_errors"] * match_stats["clear_errors"]
        + weights["var_overturns"] * match_stats["var_overturns"]
        + weights["foul_management"] * match_stats["foul_management"]
        + weights["time_in_play"] * (match_stats["time_in_play"] / 90)
    )

    # Scale and clamp base score to 1–10 range
    base_rating = max(1.0, min(10.0, 5.0 + base_score * 10))

    # --- Apply Match Difficulty Rating (MDR) ---
    mdr = compute_match_difficulty(match_context)

    final_rating = base_rating * mdr["mdr_multiplier"]
    final_rating = max(1.0, min(10.0, final_rating))

    return {
        "base_rating": round(base_rating, 2),
        "mdr_score": mdr["mdr_score"],
        "mdr_multiplier": mdr["mdr_multiplier"],
        "final_rating": round(final_rating, 2)
    }


# --- Example usage ---
if __name__ == "__main__":
    # Example referee stats
    match_stats_example = {
        "correct_decisions": 0.88,  # 88% of calls correct
        "clear_errors": 0.02,       # 2% clear errors
        "var_overturns": 0.05,      # 5% overturned by VAR
        "foul_management": 0.7,     # solid game management
        "time_in_play": 82          # 82 minutes of active play
    }

    # Example match context (values between 0–1)
    match_context_example = {
        "importance": 0.8,       # important league game
        "rivalry": 0.9,          # derby match
        "attendance": 0.75,      # 75% stadium full
        "fouls": 0.6,            # medium-high intensity
        "var": 0.5,              # average VAR activity
        "dissent": 0.4,          # mild dissent
        "weather": 0.3,          # decent conditions
        "fixture_history": 0.7   # historically fiery fixture
    }

    result = compute_referee_rating(match_stats_example, match_context_example)

    print("---- Referee Rating Breakdown ----")
    print(f"Base Rating: {result['base_rating']}")
    print(f"MDR Score: {result['mdr_score']}")
    print(f"MDR Multiplier: {result['mdr_multiplier']}")
    print(f"Final Rating: {result['final_rating']}")

