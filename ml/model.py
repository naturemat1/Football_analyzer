import pandas as pd
import numpy as np

def calculate_strengths(df, decay_factor=0.015):
    """
    Calculate home/away strengths using:
    - xG
    - Recency weighting
    - Deep completions adjustment
    """

    df = df.copy()

    # Convertir fecha si no lo está
    df["date"] = pd.to_datetime(df["date"])

    # Ordenar por fecha
    df = df.sort_values("date")

    # Calcular peso por recencia
    most_recent_date = df["date"].max()
    df["days_ago"] = (most_recent_date - df["date"]).dt.days
    df["weight"] = np.exp(-decay_factor * df["days_ago"])

    # Promedios ponderados liga
    league_home_xg_avg = np.average(df["home_xg"], weights=df["weight"])
    league_away_xg_avg = np.average(df["away_xg"], weights=df["weight"])

    #league_home_shots_avg = np.average(df["home_shots"], weights=df["weight"])
    #league_away_shots_avg = np.average(df["away_shots"], weights=df["weight"])


    teams = pd.unique(df[["home_team", "away_team"]].values.ravel())

    data = []

    for team in teams:

        home_matches = df[df["home_team"] == team]
        away_matches = df[df["away_team"] == team]

        # Promedios ponderados xG
        home_attack_xg = np.average(
            home_matches["home_xg"],
            weights=home_matches["weight"]
        ) if len(home_matches) > 0 else 0

        away_attack_xg = np.average(
            away_matches["away_xg"],
            weights=away_matches["weight"]
        ) if len(away_matches) > 0 else 0

        home_defense_xg = np.average(
            home_matches["away_xg"],
            weights=home_matches["weight"]
        ) if len(home_matches) > 0 else 0

        away_defense_xg = np.average(
            away_matches["home_xg"],
            weights=away_matches["weight"]
        ) if len(away_matches) > 0 else 0

        # Deep completions adjustment
        home_deep = np.average(
            home_matches["home_deep_completions"],
            weights=home_matches["weight"]
        ) if len(home_matches) > 0 else 0

        away_deep = np.average(
            away_matches["away_deep_completions"],
            weights=away_matches["weight"]
        ) if len(away_matches) > 0 else 0

        """
        # Shots ponderados
        home_shots = np.average(
            #home_matches["home_shots"],
            weights=home_matches["weight"]
        ) if len(home_matches) > 0 else 0

        away_shots = np.average(
            #away_matches["away_shots"],
            weights=away_matches["weight"]
        ) if len(away_matches) > 0 else 0

        #home_shot_factor = home_shots / league_home_shots_avg if league_home_shots_avg > 0 else 1
        #away_shot_factor = away_shots / league_away_shots_avg if league_away_shots_avg > 0 else 1
        """

        data.append({
            "team": team,
            "home_attack_strength":
                (home_attack_xg / league_home_xg_avg) *
                (1 + home_deep * 0.005),
                #*(1 + (home_shot_factor - 1) * 0.2),

            "home_defense_strength":
                home_defense_xg / league_away_xg_avg,

            "away_attack_strength":
                (away_attack_xg / league_away_xg_avg) *
                (1 + away_deep * 0.005),
                #*(1 + (away_shot_factor - 1) * 0.2),

            "away_defense_strength":
                away_defense_xg / league_home_xg_avg,
        })

    strengths = pd.DataFrame(data)

    return strengths, league_home_xg_avg, league_away_xg_avg


def calculate_lambdas(home_team, away_team,
                      strengths,
                      league_home_xg_avg,
                      league_away_xg_avg):

    home = strengths[strengths["team"] == home_team].iloc[0]
    away = strengths[strengths["team"] == away_team].iloc[0]

    lambda_home = (
        home["home_attack_strength"]
        * away["away_defense_strength"]
        * league_home_xg_avg
    )

    lambda_away = (
        away["away_attack_strength"]
        * home["home_defense_strength"]
        * league_away_xg_avg
    )

    return lambda_home, lambda_away

def backtest_model(df, team_stats, league_home_xg_avg, league_away_xg_avg, matchup_matrix):
    
    log_losses = []
    brier_scores = []
    
    for _, row in df.iterrows():
        
        home = row["home_team"]
        away = row["away_team"]
        
        # Saltar si no tenemos stats del equipo
        if home not in team_stats["team"].values:
            continue
        if away not in team_stats["team"].values:
            continue
        
        # === Calcular lambdas base (usa tu misma lógica aquí) ===
        
        home_lambda = (
            team_stats.loc[team_stats["team"] == home, "home_attack_strength"].values[0] *
            team_stats.loc[team_stats["team"] == away, "away_defense_strength"].values[0] *
            league_home_xg_avg
        )
        
        away_lambda = (
            team_stats.loc[team_stats["team"] == away, "away_attack_strength"].values[0] *
            team_stats.loc[team_stats["team"] == home, "home_defense_strength"].values[0] *
            league_away_xg_avg
        )
        
        # === Aplicar matchup ===
        
        home_cluster = team_stats.loc[team_stats["team"] == home, "cluster"].values[0]
        away_cluster = team_stats.loc[team_stats["team"] == away, "cluster"].values[0]
        
        factor = matchup_matrix[home_cluster][away_cluster]
        
        home_lambda *= factor
        away_lambda *= factor
        
        # === Simulación rápida Poisson (sin Monte Carlo para speed) ===
        
        from scipy.stats import poisson
        
        max_goals = 6
        
        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]
        
        home_win = 0
        draw = 0
        away_win = 0
        
        for i in range(max_goals):
            for j in range(max_goals):
                p = home_probs[i] * away_probs[j]
                if i > j:
                    home_win += p
                elif i == j:
                    draw += p
                else:
                    away_win += p
        
        probs = np.array([home_win, draw, away_win])
        probs = probs / probs.sum()
        
        # === Resultado real ===
        
        if row["home_goals"] > row["away_goals"]:
            actual = np.array([1,0,0])
        elif row["home_goals"] == row["away_goals"]:
            actual = np.array([0,1,0])
        else:
            actual = np.array([0,0,1])
        
        # === Log loss ===
        eps = 1e-15
        log_loss = -np.sum(actual * np.log(probs + eps))
        log_losses.append(log_loss)
        
        # === Brier ===
        brier = np.sum((probs - actual)**2)
        brier_scores.append(brier)
    
    return np.mean(log_losses), np.mean(brier_scores)

