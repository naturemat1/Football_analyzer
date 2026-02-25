# scrapers/fbref_scraper.py
import soccerdata as sd
import pandas as pd
import logging
from typing import Optional, Dict, List, Union

class FBrefScraper:
    """
    Wrapper for soccerdata.FBref scraper
    """
    
    def __init__(self, league: str, season: str = "2324"):
        """
        Initialize FBref scraper
        
        Args:
            league: League code (e.g., 'ENG-Premier League')
            season: Season code (e.g., '2324' for 2023-24)
        """
        self.league = league
        self.season = season
        self.scraper = sd.FBref(leagues=[league], seasons=[season])
        
    def get_schedule(self) -> Optional[pd.DataFrame]:
        """Get match schedule"""
        try:
            return self.scraper.read_schedule()
        except Exception as e:
            logging.error(f"Error getting schedule from FBref: {e}")
            return None
    
    def get_team_season_stats(self, stat_type: str = "standard") -> Optional[pd.DataFrame]:
        """
        Get team season statistics
        
        Args:
            stat_type: Type of statistics ('standard', 'shooting', 'passing', 'defense', 'possession', 'keeper')
        """
        try:
            return self.scraper.read_team_season_stats(stat_type=stat_type)
        except Exception as e:
            logging.error(f"Error getting team season stats from FBref: {e}")
            return None
    
    def get_team_match_stats(self) -> Optional[pd.DataFrame]:
        """Get team match statistics"""
        try:
            return self.scraper.read_team_match_stats()
        except Exception as e:
            logging.error(f"Error getting team match stats from FBref: {e}")
            return None
    
    def get_player_season_stats(self, stat_type: str = "standard") -> Optional[pd.DataFrame]:
        """Get player season statistics"""
        try:
            return self.scraper.read_player_season_stats(stat_type=stat_type)
        except Exception as e:
            logging.error(f"Error getting player season stats from FBref: {e}")
            return None
    
    def get_player_match_stats(self) -> Optional[pd.DataFrame]:
        """Get player match statistics"""
        try:
            return self.scraper.read_player_match_stats()
        except Exception as e:
            logging.error(f"Error getting player match stats from FBref: {e}")
            return None
    
    def get_shot_events(self) -> Optional[pd.DataFrame]:
        """Get shot events"""
        try:
            return self.scraper.read_shot_events()
        except Exception as e:
            logging.error(f"Error getting shot events from FBref: {e}")
            return None
    
    def get_lineups(self) -> Optional[pd.DataFrame]:
        """Get lineups"""
        try:
            return self.scraper.read_lineup()
        except Exception as e:
            logging.error(f"Error getting lineups from FBref: {e}")
            return None