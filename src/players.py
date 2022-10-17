import logging
from espn_api.basketball import Player
from pandas import DataFrame, json_normalize, concat
from common.datetime_utils import DATESTAMP
from src.rosters import get_rosters


def get_player_stats(rosters: dict[list[Player]]) -> DataFrame:
    df = DataFrame()

    for roster in rosters.keys():
        players = rosters[roster]

        for player in players:
            data = json_normalize(player.stats)
            data["Player"] = player.name
            data["Roster"] = roster
            data["Team"] = player.proTeam
            data["Projected_fantasy_points"] = data.apply(
                lambda x: project_avg_fantasy_points(x), axis=1
            )
            df = concat([df, data])

    df.reset_index(inplace=True, drop=True)
    return df


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
        return points / counter
    except Exception as e:
        player = row["Player"]
        logging.critical(f"No stats found for {player} to project fantasy points")
        raise e


def export_stats(df: DataFrame, free_agents: bool = False) -> DataFrame:
    roster = "team"
    if free_agents:
        roster = "freeagent"
    file_name = f"data/player/{roster}_{DATESTAMP}.csv"
    df.to_csv(file_name)
    logging.info(f"Exported dataframe as: {file_name}")
    return df


def main_team_players(debug: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    rosters = get_rosters()
    df = get_player_stats(rosters)
    export_stats(df)
    return df


def main_free_agents(debug: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    free_agents = get_rosters(free_agents=True, nr_of_free_agents=100)
    df = get_player_stats(free_agents)
    export_stats(df, free_agents=True)
    return df


def main_all_players():
    df1 = main_team_players(True)
    df2 = main_free_agents(True)
    return concat([df1, df2])


if __name__ == "__main__":
    main_all_players()
