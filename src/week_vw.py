import logging
from pandas import DataFrame
from common.datetime_utils import DATESTAMP
from common.constants import TEAMS
from common.sqlite import sqlite3_conn
from src.schedule import get_schedule


def find_opponent(row, day_of_week):
    opponent = None
    if row["dayofweek"] == day_of_week:
        if row["side"] == "home":
            opponent = "@" + row["opponent"]
        else:
            opponent = row["opponent"]
    return opponent


def transpose_schedule(df: DataFrame) -> DataFrame:
    for d in range(0, 7):
        df[d] = df.apply(lambda x: find_opponent(x, d), axis=1)
    df["gamecount"] = 1
    return df


def create_week_view(df: DataFrame) -> DataFrame:
    df = df.rename(
        columns={
            0: "monday",
            1: "tuesday",
            2: "wednesday",
            3: "thursday",
            4: "friday",
            5: "saturday",
            6: "sunday",
        }
    )

    cols = [
        "week",
        "team",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "gamecount",
    ]
    df = df[cols]
    week_view = DataFrame()
    records = []

    for team in TEAMS.values():
        _df = df.loc[df["team"] == team]

        for week in df["week"].unique():
            __df = _df.loc[_df["week"] == week]
            monday = __df["monday"].fillna("").max()
            tuesday = __df["tuesday"].fillna("").max()
            wednesday = __df["wednesday"].fillna("").max()
            thursday = __df["thursday"].fillna("").max()
            friday = __df["friday"].fillna("").max()
            saturday = __df["saturday"].fillna("").max()
            sunday = __df["sunday"].fillna("").max()
            game_count = __df["gamecount"].sum()

            record = {
                "week": week,
                "team": team,
                "monday": monday,
                "tuesday": tuesday,
                "wednesday": wednesday,
                "thursday": thursday,
                "friday": friday,
                "saturday": saturday,
                "sunday": sunday,
                "gamecount": game_count,
            }
            records.append(record)

    week_view = DataFrame().from_records(records)
    return week_view


def export_game_schedule(df: DataFrame) -> DataFrame:
    df.to_csv(f"data/schedule/week_{DATESTAMP}.csv")


def main_week_vw(debug: bool = False) -> DataFrame:
    logging.basicConfig(level=logging.WARNING)
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    df = get_schedule()
    df = transpose_schedule(df)
    df = create_week_view(df)
    sqlite3_conn.df_to_sql_table(
        df=df,
        table="week_vw",
        auto_id_cols=["week", "team"],
        if_exists="replace",
    )
    return df


if __name__ == "__main__":
    main_week_vw(True)
