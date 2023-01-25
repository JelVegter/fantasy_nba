import logging
from src.league import league, refresh_league
from espn_api.basketball import League
from pandas import DataFrame
from common.utils import ETL


class RosterETL(ETL):
    def __init__(self, league: League, free_agents: bool = False) -> None:
        self.free_agents = free_agents
        self.league = league
        super().__init__()

    def fetch_data(
        self,
    ) -> DataFrame:

        if self.free_agents:
            rosters = {"free_agents": self.league.free_agents(100)}
            self.df = DataFrame.from_dict(rosters, orient="columns")
        else:
            rosters = {team.team_name: team.roster for team in self.league.teams}
            self.df = DataFrame.from_dict(rosters, orient="index").transpose()

        return self.df

    def clean_data():
        ...

    def transform_data():
        ...

    def get_data(self):
        self.fetch_data()
        return self.df


def main_team_rosters(debug: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    league = refresh_league()
    roster = RosterETL(league=league)
    roster.get_data()
    return roster.df


def main_free_agent_rosters(debug: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    roster = RosterETL(
        league=league,
        free_agents=True,
    )
    roster.get_data()
    return roster.df


if __name__ == "__main__":
    logging.critical(main_team_rosters())
    logging.critical(main_free_agent_rosters())
