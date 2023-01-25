from schedule import ScheduleETL
from common.constants import MONTHS, TEAMS
from common.datetime_utils import DATESTAMP
from common.sqlite import sqlite3_conn
from src.league import YEAR
from pandas import DataFrame, concat
import logging


def get_data() -> DataFrame:
    amplifier = ScheduleETL()
    amplifier.fetch_data(year=YEAR, months=MONTHS)
    amplifier.clean_data()
    amplifier.df = amplifier.df.loc[~amplifier.df["pts"].isna()]
    return amplifier.df


def calculate_amplifier(df: DataFrame) -> DataFrame:
    records = []
    for team in TEAMS.values():
        home_points_against = df.loc[df["home"] == team]["pts"].sum()
        visitor_points_against = df.loc[df["visitor"] == team]["pts.1"].sum()
        records.append((team, home_points_against, visitor_points_against))

    df = DataFrame(records)
    df.columns = ["team", "home_against", "visitor_against"]
    seasonal_index = concat([df["home_against"], df["visitor_against"]]).mean()
    df["home_amp"] = df["home_against"] / seasonal_index
    df["visitor_amp"] = df["visitor_against"] / seasonal_index
    return df[["team", "home_amp", "visitor_amp"]]


def main():
    df = get_data()
    df = calculate_amplifier(df)
    sqlite3_conn.df_to_sql_table(
        df=df, table="amplifier", auto_id_cols=["team"], if_exists="replace"
    )
    logging.info(df)
    return df


if __name__ == "__main__":
    main()
