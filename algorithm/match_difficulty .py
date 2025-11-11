"""
match_difficulty.py
Elite Match Difficulty Rating (MDR) module.

Usage:
    from match_difficulty import compute_match_difficulty, compute_importance_score

This module expects per-match inputs (either a dict or pandas Series/row) containing:
- team_points_home, team_points_away : ints
- objective_points_home, objective_points_away : ints (points threshold e.g. relegation_line / promotion_line)
- games_left_home, games_left_away : ints
- is_rivalry : bool or 0/1
- stadium_capacity : int
- attendance : int
- max_league_attendance : int (for normalization)
- avg_fouls_home, avg_fouls_away : floats (recent historic averages)
- league_avg_fouls : float
- team1_avg_var_incidents, team2_avg_var_incidents : floats
- league_avg_var_incidents : float
- team_dissent_cards, manager_dissent_cards : ints (recent window)
- league_avg_dissent : float
- weather : str (one of "normal","rain","snow","heat","heavy rain")
- fixture_avg_cards : float (historical average cards in this fixture)
- league_avg_cards : float

The module converts all inputs to 0..1 sub-scores and then combines them into
a single MDR multiplier in range [0.8, 1.8] by default.
"""

from typing import Union, Dict
import math

DEFAULT_MAX_DIFFICULTY = 1.8
DEFAULT_MIN_DIFFICULTY = 0.8

def _clamp01(x):
    return max(0.0, min(1.0, float(x)))

def compute_importance_score(team_points: int, objective_points: int, games_left: int, max_gap: float = 30.0) -> float:
    """
    Compute a normalized 'importance' score in [0,1].
    - If team_points is close to objective_points given games_left, importance rises.
    - max_gap defines the scale of points difference considered (default 30).
    """
    if games_left <= 0:
        # If no games left, importance is minimal (or we could treat as already decided)
        return 0.0
    gap = abs(objective_points - team_points)
    # scale by possible points left (3 * games_left) but control with max_gap
    scaled = 1.0 - (gap / max(max_gap, 1.0))
    return _clamp01(scaled)

def compute_attendance_pressure(attendance: int, stadium_capacity: int, max_league_attendance: int) -> float:
    """
    Combine stadium capacity percentage and absolute attendance to a 0..1 score.
    - capacity component weight 0.7
    - attendance component weight 0.3
    """
    if stadium_capacity <= 0 or max_league_attendance <= 0:
        return 0.0
    capacity_pct = attendance / stadium_capacity
    attendance_norm = attendance / max_league_attendance
    score = 0.7 * _clamp01(capacity_pct) + 0.3 * _clamp01(attendance_norm)
    return _clamp01(score)

def compute_foul_intensity(avg_fouls_home: float, avg_fouls_away: float, league_avg_fouls: float) -> float:
    """
    Predicted foul frequency intensity normalized to 0..1.
    """
    if league_avg_fouls <= 0:
        return 0.0
    predicted = (avg_fouls_home + avg_fouls_away) / 2.0
    score = predicted / league_avg_fouls
    return _clamp01(score)

def compute_var_intensity(team1_var: float, team2_var: float, league_avg_var: float) -> float:
    """
    VAR involvement intensity normalized to 0..1
    """
    if league_avg_var <= 0:
        return 0.0
    avg = (team1_var + team2_var) / 2.0
    return _clamp01(avg / league_avg_var)

def compute_dissent_score(team_dissent_cards: int, manager_dissent_cards: int, league_avg_dissent: float) -> float:
    """
    Dissent score normalized to 0..1.
    If league_avg_dissent is zero or missing, returns 0.
    """
    if league_avg_dissent <= 0:
        return 0.0
    score = (team_dissent_cards + manager_dissent_cards) / league_avg_dissent
    return _clamp01(score)

def compute_weather_score(weather: str) -> float:
    """
    Convert weather category to a 0..1 difficulty score.
    - heavy_rain: 0.7
    - rain: 0.5
    - snow / extreme heat: 0.5
    - normal: 0.0
    """
    if not weather:
        return 0.0
    w = str(weather).lower()
    if "heavy" in w and "rain" in w:
        return 0.7
    if "rain" in w:
        return 0.5
    if "snow" in w or "heat" in w or "hot" in w:
        return 0.5
    return 0.0

def compute_fixture_history_score(fixture_avg_cards: float, league_avg_cards: float) -> float:
    if league_avg_cards <= 0:
        return 0.0
    score = fixture_avg_cards / league_avg_cards
    return _clamp01(score)

def compute_match_difficulty(inputs: Union[Dict, object],
                             weights: Dict[str, float] = None,
                             min_multiplier: float = DEFAULT_MIN_DIFFICULTY,
                             max_multiplier: float = DEFAULT_MAX_DIFFICULTY) -> float:
    """
    Compute the Match Difficulty Rating (MDR) multiplier.

    inputs: dictionary-like object with all required fields (see top of file).
    weights: optional dict with keys:
        'importance', 'rivalry', 'attendance', 'fouls', 'var', 'dissent', 'weather', 'fixture_history'
      If None default elite weights are used.

    Returns: multiplier between min_multiplier and max_multiplier.
    """

    # default weights (sum to 1.0)
    default_weights = {
        'importance': 0.25,
        'rivalry': 0.20,
        'attendance': 0.15,
        'fouls': 0.10,
        'var': 0.10,
        'dissent': 0.10,
        'weather': 0.05,
        'fixture_history': 0.05
    }
    w = default_weights if weights is None else {**default_weights, **weights}

    # read values safely from inputs (works if inputs is dict or pandas Series)
    get = lambda k, default=0: inputs.get(k, default) if isinstance(inputs, dict) else getattr(inputs, k, default)

    # importance: compute for both teams and take the max (higher pressure side)
    home_importance = compute_importance_score(get('team_points_home', 0), get('objective_points_home', 0), get('games_left_home', 0))
    away_importance = compute_importance_score(get('team_points_away', 0), get('objective_points_away', 0), get('games_left_away', 0))
    importance_score = max(home_importance, away_importance)

    rivalry_flag = 1.0 if (get('is_rivalry', False) in [True, 1, '1', 'true', 'True']) else 0.0

    attendance_score = compute_attendance_pressure(get('attendance', 0), get('stadium_capacity', 1), get('max_league_attendance', 1))

    fouls_score = compute_foul_intensity(get('avg_fouls_home', 0.0), get('avg_fouls_away', 0.0), get('league_avg_fouls', 1.0))

    var_score = compute_var_intensity(get('team1_avg_var_incidents', 0.0), get('team2_avg_var_incidents', 0.0), get('league_avg_var_incidents', 1.0))

    dissent_score = compute_dissent_score(get('team_dissent_cards', 0), get('manager_dissent_cards', 0), get('league_avg_dissent', 1.0))

    weather_score = compute_weather_score(get('weather', 'normal'))

    fixture_history_score = compute_fixture_history_score(get('fixture_avg_cards', 0.0), get('league_avg_cards', 1.0))

    # weighted sum of normalized components
    combined = (
        importance_score * w['importance'] +
        rivalry_flag * w['rivalry'] +
        attendance_score * w['attendance'] +
        fouls_score * w['fouls'] +
        var_score * w['var'] +
        dissent_score * w['dissent'] +
        weather_score * w['weather'] +
        fixture_history_score * w['fixture_history']
    )

    # map combined (0..1) into multiplier range by baseline min + combined*(max-min)
    multiplier = min_multiplier + combined * (max_multiplier - min_multiplier)

    # final clamp
    multiplier = max(min_multiplier, min(max_multiplier, multiplier))
    return round(multiplier, 3)
