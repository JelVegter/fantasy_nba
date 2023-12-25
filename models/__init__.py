from data.db import DB_ENGINE
from models.base import Base
from models.league import League
from models.fantasy_roster import FantasyRoster
from models.player import Player
from models.schedule import Schedule
from models.team import Team

if __name__ == "__main__":
    Base.metadata.create_all(bind=DB_ENGINE)

__all__ = [League, FantasyRoster, Player, Schedule, Team]
