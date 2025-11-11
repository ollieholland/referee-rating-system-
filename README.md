# ⚽ Referee Rating System (Mobile App + Analytics Engine)

**Created by:** Oliver Holland  
**Mission:** Referees get assessed. Fans get answers. Football gets transparency.

---

## 🚀 Overview

Football players get rated. Managers get rated.  
Referees don’t — until now.

The **Referee Rating System** is a mobile app and analytics engine that evaluates referee performance using real, quantifiable match data. Instead of emotional fan opinions or subjective media commentary, this project brings **objectivity and accountability** to refereeing.

This project combines:

- Sports analytics  
- Product development  
- Data engineering & algorithm design  
- Mobile app UI (Flutter, coming next)

Built with the mindset of a startup.

---

## 🧠 How the rating works

Each referee receives a **rating from 1.00 to 10.00**, based on weighted performance metrics:

| Category | Weight | Description |
|----------|--------|-------------|
| ✅ **Decision Accuracy** | **40%** | % of correct decisions (fouls, cards, penalties, offsides) |
| 🚫 **Foul Management** | **30%** | Controls game flow, punishes repeat fouls, applies cards consistently |
| 📺 **VAR Handling** | **15%** | Accuracy on VAR-reviewed decisions + overturn rate |
| ⏱ **Game Flow** | **15%** | % of time the ball is actively in play (keeps match moving) |

**Rating formula:**

final_rating =
(0.40 × decision_accuracy_score)

(0.30 × foul_management_score)

(0.15 × var_accuracy_score)

(0.15 × game_flow_score)


All ratings allow decimals for precise comparison across referees.

---

## 📊 Included Data (Top 5 European leagues)

Dataset contains:

- 50 referees (10 per league)
- 400+ matches
- Per-match and per-referee averages

Data files (stored in `/data/` folder):

| File | Description |
|------|-------------|
| `match_ratings_top5_50refs.csv` | Every match with rating + underlying stats |
| `referee_aggregates_top5_50refs.csv` | Season average & last 5 matches |
| `leaderboard_top5_50refs.csv` | League rankings |

Example fields:

referee_name, league, correct_decisions, clear_errors,
var_reviews, var_overturns, foul_management_score,
game_flow_score, calculated_rating

---

## 🛠 Architecture

Flutter Mobile App (UI)
↓
Python Algorithm (Rating engine)
↓
Dataset (Referee + match analytics)


Planned backend: Firebase / Supabase

---

## 💡 Why this project matters

Football is the biggest sport on Earth, yet referee performance is:

- Hard to analyse
- Extremely subjective
- Influenced by fan emotion + media narratives

This app introduces **data-driven transparency** into an area where bias is common.

---

## 📈 Future roadmap

| Phase | Feature | Status |
|--------|---------|--------|
| ✅ Phase 1 | Rating engine + dataset | Completed |
| 🔄 Phase 2 | Flutter UI screens | In progress |
| 🔜 Phase 3 | User ratings + comments | Planned |
| 🔜 Phase 4 | AI match incident detection (computer vision) | Planned |

---

## 🧩 Skills Demonstrated

- Data modeling & relational structuring
- Algorithm design & weighting logic
- Flutter development (mobile app UX/UI)
- Version control (Git + GitHub)
- Product & business thinking — sports tech use case

---

## ⭐ Vision

This system allows:

- Fans to see referee performance over time
- Analysts to compare referees statistically
- Clubs to understand referee tendencies pre-match

No more speculation.  
No more bias.  
Just data.

> Feedback and collaboration welcome





