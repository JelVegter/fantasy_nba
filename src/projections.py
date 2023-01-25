from datetime import timedelta
from pandas import DataFrame
from common.datetime_utils import TODAY, TODAY_NP, CURRENTWEEKNUMBER
from src.schedule import get_schedule
from common.sqlite import sqlite3_conn
from numpy import datetime64, where


def project_player_fantasy_points_per_period(
    players: DataFrame,
    week_number: int = 42
    # players: list[str] = None, week_number: int = 42
) -> DataFrame:

    # TODO write all df's to sql and query here
    players_df = players[["player", "team", "roster", "projected_fantasy_points"]]
    schedule_df = get_schedule()
    amplifier_df = sqlite3_conn.sql_table_to_df("amplifier")
    df = schedule_df.merge(
        amplifier_df,
        how="left",
        left_on="opponent",
        right_on="team",
        suffixes=("", "_y"),
    )

    # if players:
    #     players_df = players_df.loc[players_df["Player"] in players]

    next_week_number = week_number + 1 if not week_number == 52 else 1
    weeks = [week_number, next_week_number]

    df = df.loc[df["week"].isin(weeks)]
    df = df.loc[df["date"] >= TODAY_NP]
    df = players_df.merge(df, how="left", on="team")

    # When side is home, the opponent is visitor, thus use visitor_amp
    df["amped_projected_fantasy_points"] = where(
        df["side"] == "home",
        df["projected_fantasy_points"] * df["visitor_amp"],
        df["projected_fantasy_points"] * df["home_amp"],
    )

    # Points projected per time period
    Players = []
    ThisWeek = []
    NextWeek = []
    Today = []
    NextTwoDays = []

    for player in df["player"].unique():
        _df = df.loc[df["player"] == player]
        _df.to_csv("_df.csv")

        # To add amplifier, first calculate Projected_fantasy_points times opponent amplifier
        this_week = _df.loc[_df["week"] == week_number]
        points_this_week = this_week["amped_projected_fantasy_points"].sum()

        next_week = _df.loc[_df["week"] == next_week_number]
        points_next_week = next_week["amped_projected_fantasy_points"].sum()

        today = _df.loc[_df["date"] == TODAY_NP]
        points_today = today["amped_projected_fantasy_points"].sum()

        next_two_days = _df.loc[
            (_df["date"] >= TODAY_NP)
            & (_df["date"] <= datetime64(TODAY + timedelta(days=1)))
        ]
        points_next_two_days = next_two_days["amped_projected_fantasy_points"].sum()

        Players.append(player)
        ThisWeek.append(int(points_this_week))
        NextWeek.append(int(points_next_week))
        Today.append(int(points_today))
        NextTwoDays.append(int(points_next_two_days))

    projected_points_per_period = DataFrame(
        {
            "player": Players,
            "today": Today,
            "nexttwodays": NextTwoDays,
            "thisweek": ThisWeek,
            "nextweek": NextWeek,
        }
    )
    return projected_points_per_period


def point_projections():
    return project_player_fantasy_points_per_period(CURRENTWEEKNUMBER)
