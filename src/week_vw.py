import logging
from pandas import read_csv, DataFrame
from common.datetime_utils import DATESTAMP
from common.constants import TEAMS
from pprint import pprint


def get_schedule():
    return read_csv(f"data/schedule/schedule_{DATESTAMP}.csv", index_col=[0])


def find_opponent(row, day_of_week):
    opponent = ""
    if row["DayOfWeek"] == day_of_week:
        if row["Side"] == "Home":
            opponent = "@" + row["Opponent"]
        else:
            opponent = row["Opponent"]
    return opponent


def transpose_schedule(df: DataFrame) -> DataFrame:
    for d in range(0, 7):
        df[d] = df.apply(lambda x: find_opponent(x, d), axis=1)
    df["GameCount"] = 1
    return df


def create_week_view(df: DataFrame) -> DataFrame:
    df = df.rename(
        columns={
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
    )
    cols = [
        "Week",
        "Team",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "GameCount",
    ]
    df = df[cols]
    week_view = DataFrame()
    records = []

    for team in TEAMS.values():
        _df = df.loc[df["Team"] == team]

        for week in df["Week"].unique():
            __df = _df.loc[_df["Week"] == week]
            monday = __df["Monday"].max()
            tuesday = __df["Tuesday"].max()
            wednesday = __df["Wednesday"].max()
            thursday = __df["Thursday"].max()
            friday = __df["Friday"].max()
            saturday = __df["Saturday"].max()
            sunday = __df["Sunday"].max()
            game_count = __df["GameCount"].sum()

            record = {
                "Week": week,
                "Team": team,
                "Monday": monday,
                "Tuesday": tuesday,
                "Wednesday": wednesday,
                "Thursday": thursday,
                "Friday": friday,
                "Saturday": saturday,
                "Sunday": sunday,
                "GameCount": game_count,
            }
            records.append(record)

    week_view = DataFrame().from_records(records)
    logging.debug(pprint(week_view))
    return week_view


def export_game_schedule(df: DataFrame) -> DataFrame:
    df.to_csv(f"data/schedule/week_{DATESTAMP}.csv")


def weekvw_main(debug: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    df = get_schedule()
    df = transpose_schedule(df)
    df = create_week_view(df)
    export_game_schedule(df)
    return df


if __name__ == "__main__":
    weekvw_main(True)
