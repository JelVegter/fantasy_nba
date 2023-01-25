import asyncio
import aiohttp
import requests
from pandas import DataFrame, read_html, concat, to_datetime, read_csv
import os.path
import logging
from logging.config import fileConfig

from common.datetime_utils import DATESTAMP
from common.constants import MONTHS, TEAMS
from common.sqlite import sqlite3_conn
from common.utils import ETL
from src.league import YEAR

fileConfig("logging.ini")
logger = logging.getLogger("dev")


async def fetch(session, url: str):
    async with session.get(url, ssl=False) as response:
        data = await response.text()
        return data


async def fetch_api_data(urls: list) -> tuple:
    logging.info("Fetching api data...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        responses = await asyncio.gather(*tasks, return_exceptions=False)
    return responses


class ScheduleETL(ETL):
    def __init__(self) -> None:
        super().__init__()

    def fetch_data(self, year: int, months: list[str]) -> DataFrame:
        base_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"
        urls = [base_url.format(year, month) for month in months]
        urls_content = [requests.get(url).content for url in urls]

        html_tables = []
        for i, content in enumerate(urls_content):
            try:
                html_tables.append(read_html(content)[0])
            except Exception as e:
                logging.warning(f"{e} - {urls[i]}")

        self.df = concat(html_tables)
        return self.df

    def clean_data(self) -> DataFrame:
        self.df.columns = self.df.columns.str.lower()
        self.df["date"] = to_datetime(self.df["date"], errors="coerce").dt.tz_localize(
            tz="US/Eastern"
        )
        self.df["week"] = self.df["date"].dt.isocalendar().week
        self.df["dayofweek"] = self.df["date"].dt.dayofweek
        self.df["date"] = self.df["date"].dt.date
        self.df["visitor"] = self.df["visitor/neutral"].map(abbreviate_team)
        self.df["home"] = self.df["home/neutral"].map(abbreviate_team)
        return self.df

    def transform_data(self):
        cols = ["date", "week", "dayofweek", "start (et)", "visitor", "home"]
        self.df = self.df[cols]
        self.df["matchup"] = self.df.apply(
            lambda x: x["visitor"] + "@" + x["home"], axis=1
        )
        home = self.df.rename(columns={"home": "team", "visitor": "opponent"})
        home["side"] = "home"
        visitor = self.df.rename(columns={"visitor": "team", "home": "opponent"})
        visitor["side"] = "visitor"
        self.df = concat([home, visitor])
        return self.df

    def get_data(self, year: int, months: list[str]) -> DataFrame:
        self.fetch_data(year=year, months=months)
        self.clean_data()
        self.transform_data()
        return self.df


def abbreviate_team(team: str) -> str:
    return TEAMS[team]


def main_schedule(debug: bool = False):
    logging.basicConfig(level=logging.WARNING)
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    schedule = ScheduleETL()
    schedule.get_data(year=YEAR, months=MONTHS)
    sqlite3_conn.df_to_sql_table(
        df=schedule.df,
        table="schedule",
        auto_id_cols=["date", "matchup"],
        if_exists="replace",
    )
    return schedule.df


def get_schedule() -> DataFrame:
    return sqlite3_conn.sql_table_to_df("schedule", date_cols=["date"])


if __name__ == "__main__":
    main_schedule(True)
