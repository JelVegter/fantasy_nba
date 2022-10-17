import logging
from src.league import league
from espn_api.basketball import League, Team, Player
from pandas import DataFrame
from common.datetime_utils import DATESTAMP


def get_rosters(
    league: League = league,
    free_agents: bool = False,
    nr_of_free_agents: int = 100,
) -> dict[str, list[Player]]:
    """Function to get players in roster for teams or the free agent pool"""

    if free_agents:
        return {"free_agents": league.free_agents(nr_of_free_agents)}
    return {team.team_name: team.roster for team in league.teams}


def rosters_to_dataframe(rosters: dict[str, list[Player]]) -> DataFrame:
    df = DataFrame.from_dict(rosters, orient="columns")
    return df


def export_rosters(df: DataFrame, free_agents: bool = False) -> DataFrame:
    roster = "team"
    if free_agents:
        roster = "freeagent"
    file_name = f"data/roster/{roster}_{DATESTAMP}.csv"
    df.to_csv(file_name)
    logging.info(f"Exported dataframe as: {file_name}")
    return df


def main(debug: bool = False) -> list[Team]:
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    # Team rosters
    rosters = get_rosters()
    df = rosters_to_dataframe(rosters)
    export_rosters(df)

    # Free agent rosters
    free_agents = get_rosters(free_agents=True, nr_of_free_agents=100)
    df = rosters_to_dataframe(free_agents)
    export_rosters(df, free_agents=True)

    return rosters


if __name__ == "__main__":
    main(True)
