# data/datahub.py
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
import json

# Importar todos los scrapers
from scrapers.understat_scraper import get_data as get_understat_data
from scrapers.fbref_scraper import FBrefScraper
from scrapers.sofascore_scraper import SofascoreScraper

class DataHub:
    """
    DataHub centralizado que combina datos de múltiples fuentes
    Arquitectura modular tipo microservicios - cada scraper es independiente
    """
    
    def __init__(self, league: str, season: str = "2324"):
        """
        Inicializa el DataHub con todos los scrapers
        
        Args:
            league: Código de liga (ej. 'ENG-Premier League')
            season: Código de temporada (ej. '2324' para 2023-24)
        """
        self.league = league
        self.season = season
        
        # Inicializar scrapers (cada uno es un "microservicio" independiente)
        self._init_scrapers()
        
        # Diccionario para cachear datos
        self._cache = {}
        
        # Mapeo de nombres de equipos entre diferentes fuentes
        self.team_mappings = self._load_team_mappings()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _init_scrapers(self):
        """Inicializa todos los scrapers"""
        try:
            # Understat (usando tu función get_data)
            self.understat = lambda: get_understat_data(self.league)
            
            # FBref
            self.fbref = FBrefScraper(self.league, self.season)
            
            # Sofascore
            self.sofascore = SofascoreScraper(self.league, self.season)
            
            self.logger.info("✅ Scrapers inicializados correctamente")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando scrapers: {e}")
    
    def _load_team_mappings(self) -> Dict[str, str]:
        """
        Carga o crea mapeos de nombres de equipos entre diferentes fuentes
        """
        # Intenta cargar desde archivo
        try:
            with open('data/team_mappings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Mapeos por defecto para equipos comunes
            default_mappings = {
                # Premier League
                "Manchester United": ["Manchester Utd", "Man United", "MUFC", "Manchester United"],
                "Manchester City": ["Man City", "Manchester City", "MCI"],
                "Liverpool": ["Liverpool", "LIV"],
                "Chelsea": ["Chelsea", "CHE"],
                "Arsenal": ["Arsenal", "ARS"],
                "Tottenham": ["Tottenham Hotspur", "Spurs", "Tottenham", "TOT"],
                "Newcastle United": ["Newcastle", "Newcastle United", "NEW"],
                "Aston Villa": ["Aston Villa", "AVL"],
                "West Ham United": ["West Ham", "West Ham United", "WHU"],
                "Brighton": ["Brighton & Hove Albion", "Brighton", "BHA"],
                "Wolves": ["Wolverhampton Wanderers", "Wolves", "WOL"],
                "Everton": ["Everton", "EVE"],
                "Nottingham Forest": ["Nottingham Forest", "Nott'm Forest", "NFO"],
                "Leicester City": ["Leicester", "Leicester City", "LEI"],
                "Crystal Palace": ["Crystal Palace", "CRY"],
                "Brentford": ["Brentford", "BRE"],
                "Fulham": ["Fulham", "FUL"],
                "Bournemouth": ["Bournemouth", "BOU"],
                
                # La Liga
                "Real Madrid": ["Real Madrid", "RMA"],
                "Barcelona": ["Barcelona", "FCB", "BAR"],
                "Atletico Madrid": ["Atlético Madrid", "Atletico Madrid", "ATM"],
                "Real Sociedad": ["Real Sociedad", "RSO"],
                "Real Betis": ["Real Betis", "BET"],
                "Villarreal": ["Villarreal", "VIL"],
                "Sevilla": ["Sevilla", "SEV"],
                "Athletic Bilbao": ["Athletic Club", "Athletic Bilbao", "ATH"],
                
                # Bundesliga
                "Bayern Munich": ["Bayern Munich", "Bayern München", "FCB", "BAY"],
                "Borussia Dortmund": ["Borussia Dortmund", "Dortmund", "BVB"],
                "RB Leipzig": ["RB Leipzig", "RBL"],
                "Bayer Leverkusen": ["Bayer Leverkusen", "B04"],
                "Eintracht Frankfurt": ["Eintracht Frankfurt", "SGE"],
                
                # Serie A
                "Juventus": ["Juventus", "JUV"],
                "Inter": ["Inter", "Internazionale", "Inter Milan", "INT"],
                "Milan": ["AC Milan", "Milan", "ACM"],
                "Napoli": ["Napoli", "NAP"],
                "Roma": ["Roma", "ROM"],
                "Lazio": ["Lazio", "LAZ"],
                
                # Ligue 1
                "Paris Saint-Germain": ["PSG", "Paris Saint-Germain", "Paris SG"],
                "Marseille": ["Marseille", "OM"],
                "Monaco": ["Monaco", "ASM"],
                "Lyon": ["Lyon", "OL"],
            }
            
            # Convertir a diccionario simple (alias -> nombre_estandar)
            mappings = {}
            for standard_name, aliases in default_mappings.items():
                for alias in aliases:
                    mappings[alias] = standard_name
                    mappings[alias.lower()] = standard_name  # Versión en minúsculas
            
            return mappings
    
    def standardize_team_name(self, team_name: str) -> str:
        """
        Estandariza el nombre de un equipo usando los mapeos
        
        Args:
            team_name: Nombre del equipo en cualquier formato
            
        Returns:
            Nombre estandarizado del equipo
        """
        if not team_name:
            return team_name
            
        # Buscar en mapeos (primero exacto, luego lowercase)
        if team_name in self.team_mappings:
            return self.team_mappings[team_name]
        
        if team_name.lower() in self.team_mappings:
            return self.team_mappings[team_name.lower()]
        
        # Si no encuentra, devolver el original
        return team_name
    
    # ==================== MÉTODOS PARA UNDERSTAT ====================
    
    def get_understat_data(self) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Obtiene datos de Understat
        
        Returns:
            Dict con schedule y team_match_stats
        """
        cache_key = 'understat'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            data = get_understat_data(self.league)
            self._cache[cache_key] = data
            self.logger.info("✅ Datos de Understat obtenidos")
            return data
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos de Understat: {e}")
            return {"schedule": None, "team_match_stats": None}
    
    def get_understat_schedule(self) -> Optional[pd.DataFrame]:
        """Obtiene el calendario de Understat"""
        data = self.get_understat_data()
        return data.get("schedule")
    
    def get_understat_team_stats(self) -> Optional[pd.DataFrame]:
        """Obtiene estadísticas de equipos de Understat"""
        data = self.get_understat_data()
        return data.get("team_match_stats")
    
    # ==================== MÉTODOS PARA FBREF ====================
    
    def get_fbref_schedule(self) -> Optional[pd.DataFrame]:
        """Obtiene calendario de FBref"""
        try:
            return self.fbref.get_schedule()
        except Exception as e:
            self.logger.error(f"❌ Error en FBref schedule: {e}")
            return None
    
    def get_fbref_team_season_stats(self, stat_type: str = "standard") -> Optional[pd.DataFrame]:
        """
        Obtiene estadísticas de temporada de equipos de FBref
        
        Args:
            stat_type: standard, shooting, passing, defense, possession, keeper
        """
        try:
            return self.fbref.get_team_season_stats(stat_type)
        except Exception as e:
            self.logger.error(f"❌ Error en FBref team season stats ({stat_type}): {e}")
            return None
    
    def get_fbref_team_match_stats(self) -> Optional[pd.DataFrame]:
        """Obtiene estadísticas por partido de FBref"""
        try:
            return self.fbref.get_team_match_stats()
        except Exception as e:
            self.logger.error(f"❌ Error en FBref team match stats: {e}")
            return None
    
    def get_fbref_player_season_stats(self, stat_type: str = "standard") -> Optional[pd.DataFrame]:
        """Obtiene estadísticas de temporada de jugadores de FBref"""
        try:
            return self.fbref.get_player_season_stats(stat_type)
        except Exception as e:
            self.logger.error(f"❌ Error en FBref player season stats: {e}")
            return None
    
    def get_fbref_shot_events(self) -> Optional[pd.DataFrame]:
        """Obtiene eventos de tiros de FBref"""
        try:
            return self.fbref.get_shot_events()
        except Exception as e:
            self.logger.error(f"❌ Error en FBref shot events: {e}")
            return None
    
    def get_fbref_lineups(self) -> Optional[pd.DataFrame]:
        """Obtiene alineaciones de FBref"""
        try:
            return self.fbref.get_lineups()
        except Exception as e:
            self.logger.error(f"❌ Error en FBref lineups: {e}")
            return None
    
    # ==================== MÉTODOS PARA SOFASCORE ====================
    
    def get_sofascore_league_table(self) -> Optional[pd.DataFrame]:
        """Obtiene tabla de liga de Sofascore"""
        try:
            return self.sofascore.get_league_table()
        except Exception as e:
            self.logger.error(f"❌ Error en Sofascore league table: {e}")
            return None
    
    def get_sofascore_schedule(self) -> Optional[pd.DataFrame]:
        """Obtiene calendario de Sofascore"""
        try:
            return self.sofascore.get_schedule()
        except Exception as e:
            self.logger.error(f"❌ Error en Sofascore schedule: {e}")
            return None
    
    # ==================== MÉTODOS COMBINADOS ====================
    
    def get_all_schedules(self) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Obtiene calendarios de todas las fuentes
        
        Returns:
            Dict con schedules de cada fuente
        """
        return {
            'understat': self.get_understat_schedule(),
            'fbref': self.get_fbref_schedule(),
            'sofascore': self.get_sofascore_schedule()
        }
    
    def get_team_data(self, team_name: str) -> Dict[str, Any]:
        """
        Obtiene todos los datos disponibles para un equipo específico
        
        Args:
            team_name: Nombre del equipo
            
        Returns:
            Dict con datos del equipo de todas las fuentes
        """
        std_name = self.standardize_team_name(team_name)
        team_data = {'standardized_name': std_name, 'original_name': team_name}
        
        # Datos de Understat
        understat_stats = self.get_understat_team_stats()
        if understat_stats is not None:
            team_understat = understat_stats[understat_stats['team'] == std_name]
            if not team_understat.empty:
                team_data['understat'] = team_understat.to_dict('records')
        
        # Datos de FBref (estadísticas de temporada)
        for stat_type in ['standard', 'shooting', 'passing', 'defense']:
            stats = self.get_fbref_team_season_stats(stat_type)
            if stats is not None:
                # Buscar por nombre estandarizado en las columnas de equipo
                team_col = next((col for col in stats.columns if 'team' in col.lower()), None)
                if team_col:
                    team_stats = stats[stats[team_col].str.contains(std_name, na=False)]
                    if not team_stats.empty:
                        team_data[f'fbref_{stat_type}'] = team_stats.iloc[0].to_dict()
        
        return team_data
    
    def get_match_data(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """
        Obtiene todos los datos disponibles para un partido específico
        
        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante
            
        Returns:
            Dict con datos del partido de todas las fuentes
        """
        home_std = self.standardize_team_name(home_team)
        away_std = self.standardize_team_name(away_team)
        
        match_data = {
            'home_team': home_std,
            'away_team': away_std,
            'original_home': home_team,
            'original_away': away_team,
            'sources': {}
        }
        
        # Buscar en Understat schedule
        understat_schedule = self.get_understat_schedule()
        if understat_schedule is not None:
            match = understat_schedule[
                (understat_schedule['home_team'] == home_std) & 
                (understat_schedule['away_team'] == away_std)
            ]
            if not match.empty:
                match_data['sources']['understat'] = match.iloc[0].to_dict()
        
        # Buscar en FBref schedule
        fbref_schedule = self.get_fbref_schedule()
        if fbref_schedule is not None:
            match = fbref_schedule[
                (fbref_schedule['home_team'].str.contains(home_std, na=False)) & 
                (fbref_schedule['away_team'].str.contains(away_std, na=False))
            ]
            if not match.empty:
                match_data['sources']['fbref'] = match.iloc[0].to_dict()
        
        return match_data
    
    def get_head_to_head(self, team1: str, team2: str, n_matches: int = 10) -> pd.DataFrame:
        """
        Obtiene enfrentamientos directos entre dos equipos
        
        Args:
            team1: Primer equipo
            team2: Segundo equipo
            n_matches: Número de partidos a obtener
            
        Returns:
            DataFrame con enfrentamientos directos
        """
        team1_std = self.standardize_team_name(team1)
        team2_std = self.standardize_team_name(team2)
        
        # Usar Understat para H2H (tiene datos históricos confiables)
        schedule = self.get_understat_schedule()
        if schedule is None:
            return pd.DataFrame()
        
        h2h = schedule[
            ((schedule['home_team'] == team1_std) & (schedule['away_team'] == team2_std)) |
            ((schedule['home_team'] == team2_std) & (schedule['away_team'] == team1_std))
        ].tail(n_matches)
        
        return h2h
    
    def get_league_overview(self) -> Dict[str, Any]:
        """
        Obtiene una vista general de la liga con datos de todas las fuentes
        
        Returns:
            Dict con overview de la liga
        """
        overview = {
            'league': self.league,
            'season': self.season,
            'sources': {}
        }
        
        # Tabla de liga de Sofascore
        overview['sources']['sofascore_table'] = self.get_sofascore_league_table()
        
        # Estadísticas de equipos de FBref
        fbref_stats = {}
        for stat_type in ['standard', 'shooting', 'possession']:
            stats = self.get_fbref_team_season_stats(stat_type)
            if stats is not None:
                fbref_stats[stat_type] = stats
        
        overview['sources']['fbref_stats'] = fbref_stats
        
        # Próximos partidos
        schedules = self.get_all_schedules()
        overview['sources']['schedules'] = schedules
        
        return overview
    
    def clear_cache(self):
        """Limpia la caché de datos"""
        self._cache.clear()
        self.logger.info("Caché limpiada")
    
    def refresh_all_data(self):
        """Refresca todos los datos limpiando caché y obteniendo datos nuevos"""
        self.clear_cache()
        self.get_understat_data()  
        self.logger.info("Datos refrescados")


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de cómo usar el DataHub
    hub = DataHub("ENG-Premier League", "2324")
    
    # Obtener datos de diferentes fuentes
    understat_data = hub.get_understat_data()
    fbref_schedule = hub.get_fbref_schedule()
    sofascore_table = hub.get_sofascore_league_table()
    
    # Obtener datos de un equipo específico
    arsenal_data = hub.get_team_data("Arsenal")
    
    # Obtener datos de un partido
    match_data = hub.get_match_data("Arsenal", "Chelsea")
    
    # Obtener enfrentamientos directos
    h2h = hub.get_head_to_head("Arsenal", "Chelsea")
    
    print("DataHub funcionando correctamente")