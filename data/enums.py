from enum import Enum
from src.espn.league import YEAR


class TeamEnum(Enum):
    ATL = "Atlanta Hawks"
    BOS = "Boston Celtics"
    BKN = "Brooklyn Nets"
    CHA = "Charlotte Hornets"
    CHI = "Chicago Bulls"
    CLE = "Cleveland Cavaliers"
    DAL = "Dallas Mavericks"
    DEN = "Denver Nuggets"
    DET = "Detroit Pistons"
    GSW = "Golden State Warriors"
    HOU = "Houston Rockets"
    IND = "Indiana Pacers"
    LAL = "Los Angeles Lakers"
    LAC = "Los Angeles Clippers"
    MEM = "Memphis Grizzlies"
    MIA = "Miami Heat"
    MIL = "Milwaukee Bucks"
    MIN = "Minnesota Timberwolves"
    NOP = "New Orleans Pelicans"
    NYK = "New York Knicks"
    OKC = "Oklahoma City Thunder"
    ORL = "Orlando Magic"
    PHL = "Philadelphia 76ers"
    PHO = "Phoenix Suns"
    POR = "Portland Trail Blazers"
    SAC = "Sacramento Kings"
    SAS = "San Antonio Spurs"
    TOR = "Toronto Raptors"
    UTA = "Utah Jazz"
    WAS = "Washington Wizards"


class StatPeriodEnum(Enum):
    FULL_SEASON = f"{YEAR}"
    FULL_SEASON_PROJECTED = f"{YEAR}_projected"
    LAST_7 = f"{YEAR}_last_7"
    LAST_15 = f"{YEAR}_last_15"
    LAST_30 = f"{YEAR}_last_30"


class StatAggregationTypeEnum(Enum):
    AVG = "avg"
    TOTAL = "total"


class StatTypeEnum(Enum):
    THREE_PT_PERCENTAGE = "3PT%"
    THREE_PT_ATTEMPT = "3PTA"
    THREE_PT_MADE = "3PTM"
    ASSIST = "AST"
    BLOCK = "BLK"
    DEFENSIVE_REBOUND = "DREB"
    FIELD_GOAL_PERCENTAGE = "FG%"
    FIELD_GOAL_ATTEMPT = "FGA"
    FIELD_GOAL_MADE = "FGM"
    FREE_THROW_PERCENTAGE = "FT%"
    FREE_THROW_ATTEMPT = "FTA"
    FREE_THROW_MADE = "FTM"
    GAMES_PLAYED = "GP"
    GAMES_STARTED = "GS"
    MINUTES = "MIN"
    MINUTES_PER_GAME = "MPG"
    OFFENSIVE_REBOUND = "OREB"
    PERSONAL_FOULS = "PF"
    POINTS = "PTS"
    REBOUNDS = "REB"
    STEALS = "STL"
    TURNOVERS = "TO"
