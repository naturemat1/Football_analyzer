import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def cluster_teams(team_stats, n_clusters=4):

    features = team_stats[[
        "home_attack_strength",
        "away_attack_strength",
        "home_defense_strength",
        "away_defense_strength"
    ]]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled)

    team_stats["cluster"] = clusters
    

    return team_stats, kmeans
