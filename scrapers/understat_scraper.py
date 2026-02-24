import soccerdata as sd

def get_data(league):

    us = sd.Understat(
        leagues=[league],
        seasons=['2526'],
        no_cache=True
    )

    schedule = us.read_schedule()
    team_match_stats = us.read_team_match_stats()

    return {
        "schedule": schedule,
        "team_match_stats": team_match_stats
    }
