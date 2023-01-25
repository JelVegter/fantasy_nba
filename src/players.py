import logging
import os
from espn_api.basketball import Player
from pandas import DataFrame, json_normalize, concat, read_csv
from common.datetime_utils import CURRENTWEEKNUMBER, DATESTAMP
from common.sqlite import sqlite3_conn
from src.rosters import main_free_agent_rosters, main_team_rosters
from common.utils import ETL
from src.projections import project_player_fantasy_points_per_period


class PlayerETL(ETL):
    def __init__(self) -> None:
        super().__init__()

    def fetch_data(self, rosters: dict[list[Player]]) -> DataFrame:
        self.df = DataFrame()

        for roster in rosters.keys():
            players = rosters[roster]

            for player in players:
                if player is None:
                    continue

                data = json_normalize(player.stats)
                data["player"] = player.name
                data["roster"] = roster
                data["team"] = player.proTeam
                data["position"] = player.position
                data["status"] = player.injuryStatus
                data["projected_fantasy_points"] = data.apply(
                    lambda x: project_avg_fantasy_points(x), axis=1
                )
                self.df = concat([self.df, data])

        self.df.reset_index(inplace=True, drop=True)
        self.df.columns = self.df.columns.str.lower()
        return self.df

    def clean_data():
        ...

    def transform_data():
        ...

    def get_data(self, rosters: dict[list[Player]], refresh: bool) -> DataFrame:
        self.fetch_data(rosters)
        return self.df

    def add_projected_points_per_period(self) -> DataFrame:
        projected_points = project_player_fantasy_points_per_period(
            self.df, CURRENTWEEKNUMBER
        )
        self.df = projected_points.merge(self.df, how="right", on="player")
        return self.df


def project_avg_fantasy_points(row: DataFrame) -> int:
    points = 0
    counter = 0
    # cols = ["2023_projected.applied_avg", "2022.applied_avg"]
    games_played = 0
    if "2023.total.GP" in row.keys():
        games_played = row["2023.total.GP"]

    point_weights = {
        "2023_projected.applied_avg": 2,
        "2022.applied_avg": 2,
        "2023.applied_avg": games_played,
        "2023_last_7.applied_avg": games_played,
        "2023_last_15.applied_avg": games_played / 2,
    }
    for stat, weight in point_weights.items():
        if stat in row.keys():
            if row[stat] > 0:
                points += row[stat] * weight
                counter += weight

    try:
        return int(points / counter)
    except Exception as e:
        player = row["Player"]
        logging.critical(f"No stats found for {player} to project fantasy points")
        raise e


def etl_roster_players(debug: bool = False, refresh: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    rosters = main_team_rosters()
    players = PlayerETL()
    players.get_data(rosters, refresh)
    players.add_projected_points_per_period()
    return players.df


def etl_free_agents(debug: bool = False, refresh: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    free_agents = main_free_agent_rosters()
    players = PlayerETL()
    players.get_data(free_agents, refresh)
    players.add_projected_points_per_period()
    return players.df


def etl_all_players():
    df1 = etl_roster_players(True)
    df2 = etl_free_agents(True)
    df = concat([df1, df2])
    sqlite3_conn.df_to_sql_table(
        df=df, table="players", auto_id_cols=["player"], if_exists="replace"
    )
    return df


def get_free_agents() -> DataFrame:
    return sqlite3_conn.sql_query_to_df(
        """ SELECT *
            FROM PLAYERS
            WHERE roster = 'free_agents'"""
    )


def get_players_on_roster() -> DataFrame:
    return sqlite3_conn.sql_query_to_df(
        """ SELECT *
            FROM PLAYERS
            WHERE roster != 'free_agents'"""
    )


if __name__ == "__main__":
    df = etl_all_players()

    logging.critical(df)
