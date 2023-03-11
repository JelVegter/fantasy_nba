from src.players import get_free_agents, get_players_on_roster, etl_all_players
from src.week_vw import main_week_vw
from src.schedule import main_schedule
from common.sqlite import sqlite3_conn
from common.datetime_utils import NOW_STR


class DataSets:
    def __init__(self) -> None:
        self.week_vw = sqlite3_conn.sql_table_to_df(
            "week_vw",
        )
        self.free_agents = get_free_agents()
        self.roster_players = get_players_on_roster()
        self.reset = False
        self.time_set = NOW_STR
        self.time_set_str = f"Data last refreshed at {self.time_set}"

    def refresh_datasets(self) -> None:
        etl_all_players()
        main_schedule()
        main_week_vw()
        self.week_vw = main_week_vw()
        self.free_agents = get_free_agents()
        self.roster_players = get_players_on_roster()
        self.time_set = NOW_STR
        self.reset = True


DATASETS = DataSets()
