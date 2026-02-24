class DataHub:

    def __init__(self, league):
        self.league = league
        self.raw_data = None
        self.master_df = None

    def load_understat(self):
        # usa tu get_data()
        pass

    def load_odds(self):
        # usar API de odds (si ya scrapeas)
        pass

    def unify(self):
        # normalizar columnas
        # merge xG + goals + odds
        pass

    def get_master(self):
        return self.master_df
