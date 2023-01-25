from src.players import get_free_agents, get_players_on_roster, etl_all_players
from src.week_vw import main_week_vw
from src.schedule import main_schedule
from common.sqlite import sqlite3_conn


class DataSets:
    def __init__(self) -> None:
        self.week_vw = sqlite3_conn.sql_table_to_df(
            "week_vw",
        )
        self.free_agents = get_free_agents()
        self.roster_players = get_players_on_roster()

    def refresh_datasets(self) -> None:
        etl_all_players()
        main_schedule()
        main_week_vw()
        self.week_vw = main_week_vw()
        self.free_agents = get_free_agents()
        self.roster_players = get_players_on_roster()


DATASETS = DataSets()
