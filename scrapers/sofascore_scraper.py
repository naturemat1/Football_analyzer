# scrapers/sofascore_scraper.py
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

class SofascoreScraper:
    """
    Scraper for Sofascore API - real-time stats, form, injuries, etc.
    """
    
    BASE_URL = "https://api.sofascore.com/api/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://www.sofascore.com'
        })
    
    def get_team_form(self, team_id, num_matches=10):
        """Get team's recent form with detailed stats"""
        url = f"{self.BASE_URL}/team/{team_id}/events/last/{num_matches}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return self._parse_form_data(data['events'])
        except Exception as e:
            logging.error(f"Error getting team form: {e}")
        return None
    
    def get_match_statistics(self, match_id):
        """Get detailed match statistics including shots, cards, etc."""
        url = f"{self.BASE_URL}/event/{match_id}/statistics"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return self._parse_match_stats(data)
        except Exception as e:
            logging.error(f"Error getting match stats: {e}")
        return None
    
    def get_head_to_head(self, home_team_id, away_team_id, num_matches=10):
        """Get head-to-head statistics between two teams"""
        url = f"{self.BASE_URL}/team/{home_team_id}/versus/{away_team_id}/statistics"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return data
        except Exception as e:
            logging.error(f"Error getting H2H data: {e}")
        return None
    
    def _parse_form_data(self, events):
        """Parse form data into structured format"""
        form_data = []
        for event in events:
            form_data.append({
                'date': event.get('startTimestamp'),
                'home_team': event['homeTeam']['name'],
                'away_team': event['awayTeam']['name'],
                'home_score': event['homeScore']['current'],
                'away_score': event['awayScore']['current'],
                'home_xg': event.get('homeTeam', {}).get('statistics', {}).get('expectedGoals'),
                'away_xg': event.get('awayTeam', {}).get('statistics', {}).get('expectedGoals'),
                'possession_home': event.get('statistics', {}).get('ballPossession'),
                'shots_home': event.get('statistics', {}).get('totalShots'),
                'shots_away': event.get('statistics', {}).get('totalShots'),
                'shots_on_target_home': event.get('statistics', {}).get('shotsOnTarget'),
                'shots_on_target_away': event.get('statistics', {}).get('shotsOnTarget')
            })
        return pd.DataFrame(form_data)
    
    def _parse_match_stats(self, data):
        """Parse detailed match statistics"""
        stats = {}
        for period in data.get('statistics', []):
            for group in period.get('groups', []):
                for item in group.get('statisticsItems', []):
                    stats[item['name']] = {
                        'home': item.get('home'),
                        'away': item.get('away')
                    }
        return stats