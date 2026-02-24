import pandas as pd

def team_averages(df):

    df = df.reset_index()

    # Local
    home_df = pd.DataFrame({
        "team": df["home_team"],
        "goals": df["home_goals"],
        "xG": df["home_xg"],
        "ppda": df["home_ppda"],
        "deep_completions": df["home_deep_completions"],
        "home": 1
    })

    # Visitante
    away_df = pd.DataFrame({
        "team": df["away_team"],
        "goals": df["away_goals"],
        "xG": df["away_xg"],
        "ppda": df["away_ppda"],
        "deep_completions": df["away_deep_completions"],
        "home": 0
    })

    combined = pd.concat([home_df, away_df])

    grouped = combined.groupby("team").mean().reset_index()
    
    league_avg_goals = combined["goals"].mean()
    print("Columnas\n",df.columns)

    print("\nPromedio goles liga:", league_avg_goals)


    # Métricas avanzadas
    grouped["finishing_efficiency"] = grouped["goals"] / grouped["xG"]

    return grouped.sort_values("goals", ascending=False)


