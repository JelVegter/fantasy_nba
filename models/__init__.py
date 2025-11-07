from data.db import DB_ENGINE
from models.base import Base
from models.league import League
from models.fantasy_roster import FantasyRoster
from models.player import Player
from models.schedule import Schedule
from models.team import Team
from models.player_stats import StatAggregation


def create_tables() -> None:
    Base.metadata.create_all(bind=DB_ENGINE)


if __name__ == "__main__":
    create_tables()

__all__ = [League, FantasyRoster, Player, Schedule, Team, StatAggregation]
