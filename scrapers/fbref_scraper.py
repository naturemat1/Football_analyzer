#NO FUNCIONAL AL MOMENTO
import soccerdata as sd

def get_data(league):

    fbref = sd.FBref(
        leagues=[league],
        seasons=['2526'],
        no_cache=True
    )

    schedule = fbref.read_schedule()
    team_stats = fbref.read_team_season_stats(stat_type="shooting")

    return {
        "schedule": schedule,
        "team_stats": team_stats
    }
