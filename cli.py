import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Football Match Predictor")

    parser.add_argument("--league", type=str, required=True,
                        help="League name (e.g. ENG-Premier League)")

    parser.add_argument("--home", type=str, required=True,
                        help="Home team")

    parser.add_argument("--away", type=str, required=True,
                        help="Away team")

    return parser.parse_args()
