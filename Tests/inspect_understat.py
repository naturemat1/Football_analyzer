from scrapers.understat_scraper import get_data


data = get_data("ENG-Premier League")

print("=== SCHEDULE COLUMNS ===")
print(data["schedule"].columns)

print("\n=== TEAM MATCH STATS COLUMNS ===")
print(data["team_match_stats"].columns)

print("\n=== SAMPLE SCHEDULE ===")
print(data["schedule"].head())

print("\n=== SAMPLE TEAM MATCH STATS ===")
print(data["team_match_stats"].head())
