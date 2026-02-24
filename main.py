import argparse
from scrapers.understat_scraper import get_data
from processing.feature_engineering import team_averages
from ml.model import calculate_strengths, calculate_lambdas, backtest_model
from ml.simulator import monte_carlo_simulation
from processing.clustering import cluster_teams

MATCHUP_MATRIX = {
    0: {0: 0.95, 1: 0.85, 2: 0.90, 3: 0.92},
    1: {0: 1.15, 1: 1.05, 2: 1.08, 3: 1.10},
    2: {0: 1.05, 1: 0.92, 2: 0.97, 3: 1.00},
    3: {0: 1.08, 1: 0.98, 2: 1.02, 3: 1.00},
}


def main():
    parser = argparse.ArgumentParser(description="Football Betting Model")

    parser.add_argument("--league", type=str, required=True,
                        help="League name (e.g. ENG-Premier League)")

    parser.add_argument("--team", type=str,
                        help="Show detailed stats for a specific team")

    parser.add_argument("--home", type=str,
                        help="Home team for match prediction")

    parser.add_argument("--away", type=str,
                        help="Away team for match prediction")

    args = parser.parse_args()

    # ===============================
    # 1️⃣ LOAD DATA
    # ===============================
    data = get_data(args.league)

    print("\n=== LEAGUE LOADED ===")
    print(data["schedule"].head())

    # ===============================
    # 2️⃣ TEAM ANALYSIS MODE
    # ===============================
    if args.team:
        print(f"\n=== MATCHES FOR {args.team} ===")

        team_matches = data["schedule"][
            (data["schedule"]["home_team"] == args.team) |
            (data["schedule"]["away_team"] == args.team)
        ]

        print(team_matches.head())

        print("\n=== TEAM MATCH STATS ===")
        print(data["team_match_stats"].head())

        averages = team_averages(data["team_match_stats"])

        print("\n=== TEAM AVERAGES ===")
        print(averages.head())

        high_scoring = averages[averages["goals"] > 2.5]

        print("\nTeams averaging over 2.5 goals:")
        print(high_scoring)

    # ===============================
    # 3️⃣ MATCH PREDICTION MODE
    # ===============================
    if args.home and args.away:

        print(f"\n=== PREDICTION: {args.home} vs {args.away} ===")

        # Calculate strengths
        team_stats, league_home_xg_avg, league_away_xg_avg = calculate_strengths(
            data["team_match_stats"]
        )

        home_lambda, away_lambda = calculate_lambdas(
            args.home,
            args.away,
            team_stats,
            league_home_xg_avg,
            league_away_xg_avg
        )

        team_stats, model = cluster_teams(team_stats)

        # BACKTEST
        log_loss, brier = backtest_model(
            data["team_match_stats"],   
            team_stats,
            league_home_xg_avg,
            league_away_xg_avg,
            MATCHUP_MATRIX
        )

        print("\n=== BACKTEST RESULTS ===")
        print(f"Log Loss: {log_loss:.4f}")
        print(f"Brier Score: {brier:.4f}")


        
        print("\n=== TEAM CLUSTERS ===")
        print(team_stats[["team", "cluster"]].head())
        numeric_cols = team_stats.select_dtypes(include=["float64", "int64"]).columns
        cluster_summary = team_stats.groupby("cluster")[numeric_cols].mean()
        print(cluster_summary)

        print(f"\nExpected Goals:")
        print(f"{args.home}: {home_lambda:.2f}")
        print(f"{args.away}: {away_lambda:.2f}")

        # Obtener clusters
        home_cluster = team_stats[team_stats["team"] == args.home]["cluster"].values[0]
        away_cluster = team_stats[team_stats["team"] == args.away]["cluster"].values[0]

        # Aplicar factor de matchup
        matchup_factor = MATCHUP_MATRIX[home_cluster][away_cluster]

        home_lambda *= matchup_factor
        away_lambda *= matchup_factor


        # Run Poisson simulation
        results = monte_carlo_simulation(home_lambda, away_lambda)



        print("\n=== PROBABILITIES ===")
        print(f"Home win: {results['home_win']:.2%}")
        print(f"Draw: {results['draw']:.2%}")
        print(f"Away win: {results['away_win']:.2%}")
        print(f"Over 2.5 goals: {results['over_2_5']:.2%}")


if __name__ == "__main__":
    main()
