# rating_algorithm.py
# Full professional referee rating model with behaviour indicators,
# difficulty scaling, consistency, form, and season averages.

import numpy as np
import pandas as pd


# ============================================================
# 1. BEHAVIOUR DEFAULTS (added if missing from dataset)
# ============================================================

BEHAVIOUR_DEFAULTS = {
    "FvX": 1.0,       # Fouls given vs expected
    "YCPF": 0.20,     # Yellow cards per foul
    "VARF": 0.10,     # VAR involvement frequency
    "HBI": 0.10,      # Home-bias index
    "CPR": 0.20,      # Crowd-pressure reactivity
    "TTD": 0.40       # Decision time (0-1)
}

def ensure_behaviour_columns(df):
    for col, val in BEHAVIOUR_DEFAULTS.items():
        if col not in df.columns:
            df[col] = val
    return df


# ============================================================
# 2. MATCH DIFFICULTY SCORE (MDS)
# ============================================================

def compute_match_difficulty(row):
    mds = (
        0.20 * row["crowd_pressure"] +
        0.15 * row["attendance_pct"] +
        0.20 * row["rivalry_intensity"] +
        0.20 * row["match_importance"] +
        0.10 * row["VARF"] +
        0.10 * row["CPR"]
    )
    return max(0.0, min(1.0, mds))


def difficulty_category(mds):
    if mds < 0.45:
        return "easy"
    elif mds > 0.55:
        return "hard"
    else:
        return "medium"


# ============================================================
# 3. BASE WEIGHTS (per difficulty mode)
# ============================================================

BASE_WEIGHTS = {
    "easy": {
        "decision_accuracy": 0.50,
        "foul_management": 0.20,
        "var_overturns": 0.05,
        "crowd_pressure": 0.05,
        "match_importance": 0.05,
        "attendance_pct": 0.05,
        "rivalry_intensity": 0.10
    },
    "medium": {
        "decision_accuracy": 0.35,
        "foul_management": 0.25,
        "var_overturns": 0.10,
        "crowd_pressure": 0.10,
        "match_importance": 0.10,
        "attendance_pct": 0.05,
        "rivalry_intensity": 0.05
    },
    "hard": {
        "decision_accuracy": 0.25,
        "foul_management": 0.25,
        "var_overturns": 0.15,
        "crowd_pressure": 0.15,
        "match_importance": 0.10,
        "attendance_pct": 0.05,
        "rivalry_intensity": 0.05
    }
}


# ============================================================
# 4. APPLY BEHAVIOURAL MODIFIERS TO WEIGHTS
# ============================================================

def apply_behaviour_modifiers(row, weights):
    w = weights.copy()

    # Behaviour modifiers
    modifier = {
        "foul_management": row["FvX"],                  # strictness
        "crowd_pressure": 1 + row["CPR"] * 0.2,         # pressure reaction
        "var_overturns": 1 + row["VARF"] * 0.3,         # VAR dependence
        "attendance_pct": 1 + row["HBI"] * 0.2,         # home bias
        "decision_accuracy": 1 - row["TTD"] * 0.1       # hesitation penalty
    }

    # Apply modifiers
    for f in w:
        w[f] *= modifier.get(f, 1.0)

    # Normalise back to sum=1
    total = sum(w.values())
    for f in w:
        w[f] /= total

    return w


# ============================================================
# 5. ERROR SEVERITY INDEX (ESI) WITH DIFFICULTY SCALING
# ============================================================

def compute_scaled_ESI(row):
    base_penalty = (
        row["minor_errors"] * -0.05 +
        row["moderate_errors"] * -0.15 +
        row["major_errors"] * -0.40
    )
    mds = compute_match_difficulty(row)
    penalty = base_penalty * (0.5 + mds)
    return penalty


# ============================================================
# 6. BASE RATING CALCULATION
# ============================================================

def compute_base_rating(row, weights):
    score = 0
    for feature, w in weights.items():
        value = row.get(feature, 0)
        score += value * w * 10
    return score


# ============================================================
# 7. FINAL RATING
# ============================================================

def compute_final_rating(row):
    mds = compute_match_difficulty(row)
    mode = difficulty_category(mds)

    base_w = BASE_WEIGHTS[mode]
    adjusted_w = apply_behaviour_modifiers(row, base_w)

    base = compute_base_rating(row, adjusted_w)
    esi_penalty = compute_scaled_ESI(row)

    final = base + esi_penalty
    final = max(1.0, min(10.0, round(final, 2)))

    return final, mds, mode


# ============================================================
# 8. CONSISTENCY BONUS
# ============================================================

def compute_consistency_bonus(df):
    bonuses = {}
    for ref in df["referee"].unique():
        ref_df = df[df["referee"] == ref].sort_values("match_id")
        rolling_std = ref_df["final_rating"].rolling(5).std()

        for idx, std in zip(ref_df.index, rolling_std):
            if np.isnan(std):
                bonuses[idx] = 0
            elif std < 0.15:
                bonuses[idx] = 0.20
            elif std < 0.30:
                bonuses[idx] = 0.10
            elif std < 0.50:
                bonuses[idx] = 0.00
            else:
                bonuses[idx] = -0.15
    return bonuses


# ============================================================
# 9. FORM + SEASON AVERAGE
# ============================================================

def compute_form_and_season(df):
    form_map = {}
    season_map = {}

    for ref in df["referee"].unique():
        matches = df[df["referee"] == ref].sort_values("match_id")
        season_map[ref] = round(matches["final_rating"].mean(), 2)

        rolling = matches["final_rating"].rolling(5).mean()
        for idx, val in zip(matches.index, rolling):
            form_map[idx] = round(val, 2) if not np.isnan(val) else None

    return form_map, season_map


# ============================================================
# 10. MASTER FUNCTION
# ============================================================

def rate_dataframe(df):

    df = ensure_behaviour_columns(df)

    # STEP 1 — apply base rating
    finals, mds_list, mode_list = [], [], []
    for _, row in df.iterrows():
        final, mds, mode = compute_final_rating(row)
        finals.append(final)
        mds_list.append(mds)
        mode_list.append(mode)

    df["final_rating"] = finals
    df["mds"] = mds_list
    df["difficulty_mode"] = mode_list

    # STEP 2 — consistency bonuses
    bonuses = compute_consistency_bonus(df)
    df["final_rating"] += df.index.map(bonuses)

    # STEP 3 — season + form
    form_map, season_map = compute_form_and_season(df)
    df["form_5_games"] = df.index.map(form_map)
    df["season_average"] = df["referee"].map(season_map)

    return df

