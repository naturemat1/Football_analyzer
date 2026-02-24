# scrapers/sofascore_scraper.py
import soccerdata as sd
import pandas as pd
import logging
from typing import Optional, Dict, List

class SofascoreScraper:
    """
    Wrapper for soccerdata.Sofascore scraper
    """
    
    def __init__(self, league: str, season: str = "2324"):
        """
        Initialize Sofascore scraper
        
        Args:
            league: League code (e.g., 'ENG-Premier League')
            season: Season code (e.g., '2324' for 2023-24)
        """
        self.league = league
        self.season = season
        self.scraper = sd.Sofascore(leagues=[league], seasons=[season])
        
    def get_league_table(self) -> Optional[pd.DataFrame]:
        """Get current league table"""
        try:
            return self.scraper.read_league_table()
        except Exception as e:
            logging.error(f"Error getting league table from Sofascore: {e}")
            return None
    
    def get_schedule(self) -> Optional[pd.DataFrame]:
        """Get match schedule"""
        try:
            return self.scraper.read_schedule()
        except Exception as e:
            logging.error(f"Error getting schedule from Sofascore: {e}")
            return None
    
    def get_leagues(self) -> List[str]:
        """Get available leagues"""
        return self.scraper.available_leagues()
    
    def get_seasons(self) -> List[str]:
        """Get available seasons"""
        return self.scraper.available_seasons(self.league) if self.league else []