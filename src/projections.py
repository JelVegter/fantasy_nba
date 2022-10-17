from pprint import pprint
from pandas import DataFrame
from common.datetime_utils import CURRENTDAYOFWEEK
from src.players import main_all_players
from src import schedule


def project_player_fantasy_points_per_week_day(
    players: list[str] = None, week_number: int = 42
) -> DataFrame:

    players_df = main_all_players()
    players_df = players_df[["Player", "Team", "Roster", "Projected_fantasy_points"]]

    schedule_df = schedule.main()

    if players:
        players_df = players_df.loc[players_df["Player"] in players]

    schedule_df = schedule_df.loc[schedule_df["Week"] == week_number]

    df = players_df.merge(schedule_df, how="left", on="Team")

    for week_number in range(0, 7):
        df[week_number] = df.apply(
            lambda x: x["Projected_fantasy_points"]
            if x["DayOfWeek"] == week_number
            else None,
            axis=1,
        )
    cols = [
        "Player",
        "Team",
        "Roster",
        "Projected_fantasy_points",
        "Week",
        0,
        1,
        2,
        3,
        4,
        5,
        6,
    ]
    df = df[cols].groupby(by=["Player", "Team", "Week", "Roster"]).sum()
    df = df.apply(
        lambda x: calculate_projected_points_next_days(x, CURRENTDAYOFWEEK), axis=1
    )
    pprint(df)
    exit()
    pprint(schedule_df)
    return schedule_df


def calculate_projected_points_next_days(
    row: DataFrame, current_day_of_week: int
) -> DataFrame:

    for iterator in range(1, 7):
        row[f"{iterator}_Days"] = 0
        for _ in range(current_day_of_week, current_day_of_week + iterator):

            if _ > 6:
                continue

            if row[_] > 0:
                row[f"{iterator}_Days"] += row[_]

    row = row.rename(columns={"1_Days": "Today"})
    pprint(row)
    return row


def main():
    project_player_fantasy_points_per_week_day()


if __name__ == "__main__":
    main()
