def print_prediction(home, away, result):

    print(f"\n=== PREDICTION: {home} vs {away} ===\n")

    print(f"Expected goals:")
    print(f"{home}: {result['lambda_home']:.2f}")
    print(f"{away}: {result['lambda_away']:.2f}\n")

    print("Probabilities:")
    print(f"Home win: {result['home_win']:.2%}")
    print(f"Draw: {result['draw']:.2%}")
    print(f"Away win: {result['away_win']:.2%}")
    print(f"Over 2.5 goals: {result['over_2_5']:.2%}")
