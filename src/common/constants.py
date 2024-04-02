from src.common.utils import fetch_data
from data.db import DB_URI
from datetime import datetime
from pytz import timezone

DEBUG_MODE = True


TIMEZONE_STR = "US/Eastern"
TIMEZONE = timezone(TIMEZONE_STR)
DATETIME = datetime.now(tz=TIMEZONE)
DATETIME_PRETTY = DATETIME.strftime("%A, %B %d, %I:%M")
DATE = DATETIME.date()
DATE_TZ_AWARE = DATETIME.replace(hour=0, minute=0, second=0, microsecond=0)
CURRENTWEEKNUMBER = DATETIME.isocalendar()[1]
CURRENTDAYOFYEAR = int(DATE_TZ_AWARE.strftime("%j"))

PLAYER_POINTS_COLS = [
    "name",
    "sum_fantasy_points",
    "games",
    "avg_points",
    "avg_last_7",
    "avg_last_15",
    "avg_last_30",
    "injury_status",
    "projected_avg_points",
    "sum_avg_points",
    "sum_proj_avg_points",
    "team_abbrev",
    "position",
]


def day_of_week_to_name(day: int) -> str:
    """Converts day of the week from number to name."""
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return weekdays[day]


def get_free_agents() -> list[str]: ...


def get_fantasy_rosters_as_list() -> list[str]:
    df = fetch_data(
        "SELECT DISTINCT(name) as name FROM fantasy_roster WHERE name != 'Free Agent'",
        DB_URI,
    )
    return df.to_dict()["name"].to_list()


# FREE_AGENTS = get_free_agents()
FANTASY_ROSTERS = get_fantasy_rosters_as_list()
