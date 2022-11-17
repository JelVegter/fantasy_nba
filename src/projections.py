from datetime import timedelta
from pandas import DataFrame
from common.datetime_utils import TODAY, CURRENTWEEKNUMBER
from src.schedule import main_schedule


def project_player_fantasy_points_per_period(
    players: DataFrame,
    week_number: int = 42
    # players: list[str] = None, week_number: int = 42
) -> DataFrame:

    players_df = players[["Player", "Team", "Roster", "Projected_fantasy_points"]]
    schedule_df = main_schedule()

    # if players:
    #     players_df = players_df.loc[players_df["Player"] in players]

    next_week_number = week_number + 1 if not week_number == 52 else 1
    weeks = [week_number, next_week_number]

    schedule_df = schedule_df.loc[schedule_df["Week"].isin(weeks)]
    schedule_df = schedule_df.loc[schedule_df["Date"] >= TODAY]
    df = players_df.merge(schedule_df, how="left", on="Team")

    # Points projected per time period
    Players = []
    ThisWeek = []
    NextWeek = []
    Today = []
    NextThreeDays = []

    for player in df["Player"].unique():
        _df = df.loc[df["Player"] == player]

        # To add amplifier, first calculate Projected_fantasy_points times opponent amplifier
        this_week = _df.loc[_df["Week"] == week_number]
        points_this_week = this_week["Projected_fantasy_points"].sum()

        next_week = _df.loc[_df["Week"] == next_week_number]
        points_next_week = next_week["Projected_fantasy_points"].sum()

        today = _df.loc[_df["Date"] == TODAY]
        points_today = today["Projected_fantasy_points"].sum()

        next_three_days = _df.loc[
            (_df["Date"] >= TODAY) & (_df["Date"] <= TODAY + timedelta(days=2))
        ]
        points_next_three_days = next_three_days["Projected_fantasy_points"].sum()

        Players.append(player)
        ThisWeek.append(int(points_this_week))
        NextWeek.append(int(points_next_week))
        Today.append(int(points_today))
        NextThreeDays.append(int(points_next_three_days))

    projected_points_per_period = DataFrame(
        {
            "Player": Players,
            "Today": Today,
            "NextThreeDays": NextThreeDays,
            "ThisWeek": ThisWeek,
            "NextWeek": NextWeek,
        }
    )
    return projected_points_per_period


def main_point_projections():
    return project_player_fantasy_points_per_period(CURRENTWEEKNUMBER)


if __name__ == "__main__":
    main_point_projections()
