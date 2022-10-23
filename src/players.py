import logging
import os
from espn_api.basketball import Player
from pandas import DataFrame, json_normalize, concat, read_csv
from common.datetime_utils import DATESTAMP
from src.rosters import main_free_agent_rosters, main_team_rosters
from common.utils import DataGetter
from src.projections import project_player_fantasy_points_per_period


class PlayerDataGetter(DataGetter):
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        super().__init__()

    def fetch_data(self, rosters: dict[list[Player]]) -> DataFrame:
        self.df = DataFrame()

        for roster in rosters.keys():
            players = rosters[roster]

            for player in players:
                if player is None:
                    continue

                data = json_normalize(player.stats)
                data["Player"] = player.name
                data["Roster"] = roster
                data["Team"] = player.proTeam
                data["Position"] = player.position
                data["Status"] = player.injuryStatus
                data["Projected_fantasy_points"] = data.apply(
                    lambda x: project_avg_fantasy_points(x), axis=1
                )
                self.df = concat([self.df, data])

        self.df.reset_index(inplace=True, drop=True)
        return self.df

    def clean_data():
        ...

    def transform_data():
        ...

    def export_data(self) -> DataFrame:
        self.df.to_csv(self.file_path)
        logging.info(f"Exported dataframe as: {self.file_path}")
        return self.df

    def read_data(self) -> DataFrame:
        self.df = read_csv(self.file_path, index_col=[0])
        return self.df

    def get_data(self, rosters: dict[list[Player]], refresh: bool) -> DataFrame:
        if os.path.isfile(self.file_path) and not refresh:
            logging.info(f"Reading existing Player data file: {self.file_path}")
            return self.read_data()

        logging.info("Creating Player data file")
        self.fetch_data(rosters)
        self.export_data()
        return self.df

    def add_projected_points_per_period(self) -> DataFrame:
        projected_points = project_player_fantasy_points_per_period(self.df)
        self.df = self.df.merge(projected_points, how="left", on="Player")
        return self.df


def project_avg_fantasy_points(row: DataFrame) -> float:
    points = 0
    counter = 0
    cols = ["2023_projected.applied_avg", "2022.applied_avg"]

    for col in cols:
        if col in row.keys():
            if row[col] > 0:
                points += row[col]
                counter += 1

    try:
        return int(points / counter)
    except Exception as e:
        player = row["Player"]
        logging.critical(f"No stats found for {player} to project fantasy points")
        raise e


def main_player_point_projections(debug: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


def main_team_players(debug: bool = False, refresh: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    rosters = main_team_rosters()
    players = PlayerDataGetter(file_path=f"data/player/team_{DATESTAMP}.csv")
    players.get_data(rosters, refresh)
    players.add_projected_points_per_period()
    return players.df


def main_free_agents(debug: bool = False, refresh: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    free_agents = main_free_agent_rosters()
    players = PlayerDataGetter(file_path=f"data/player/freeagent_{DATESTAMP}.csv")
    players.get_data(free_agents, refresh)
    players.add_projected_points_per_period()
    return players.df


def main_all_players():
    df1 = main_team_players(True)
    df2 = main_free_agents(True)
    return concat([df1, df2])


if __name__ == "__main__":
    df = main_all_players()
    logging.critical(df)
