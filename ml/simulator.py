import numpy as np


def monte_carlo_simulation(home_lambda, away_lambda,
                           n_simulations=100000,
                           lambda_uncertainty=0.10):

    home_wins = 0
    draws = 0
    away_wins = 0
    over_2_5 = 0

    for _ in range(n_simulations):

        # Añadir incertidumbre
        lambda_home_sim = np.random.normal(
            home_lambda,
            home_lambda * lambda_uncertainty
        )

        lambda_away_sim = np.random.normal(
            away_lambda,
            away_lambda * lambda_uncertainty
        )

        lambda_home_sim = max(lambda_home_sim, 0.01)
        lambda_away_sim = max(lambda_away_sim, 0.01)

        home_goals = np.random.poisson(lambda_home_sim)
        away_goals = np.random.poisson(lambda_away_sim)

        if home_goals > away_goals:
            home_wins += 1
        elif home_goals == away_goals:
            draws += 1
        else:
            away_wins += 1

        if home_goals + away_goals > 2:
            over_2_5 += 1

    return {
        "home_win": home_wins / n_simulations,
        "draw": draws / n_simulations,
        "away_win": away_wins / n_simulations,
        "over_2_5": over_2_5 / n_simulations
    }
