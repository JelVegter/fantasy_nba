from src.players import main_free_agents, main_team_players
from src.week_vw import main_week_vw


class DataSets:
    def __init__(self) -> None:
        self.week_vw = main_week_vw()
        self.free_agents = main_free_agents()
        self.roster_players = main_team_players()

    def refresh_datasets(self) -> None:
        self.week_vw = main_week_vw()
        self.free_agents = main_free_agents(refresh=True)
        self.roster_players = main_team_players(refresh=True)


DATASETS = DataSets()
