import asyncio
import aiohttp
import requests
from pandas import DataFrame, read_html, concat, to_datetime, read_csv
import os.path
import logging
from logging.config import fileConfig

from common.datetime_utils import DATESTAMP
from common.constants import MONTHS, TEAMS
from common.utils import DataGetter
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


class ScheduleDataGetter(DataGetter):
    def __init__(self, file_path) -> None:
        self.file_path = file_path
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
        self.df["Date"] = to_datetime(self.df["Date"], errors="coerce").dt.tz_localize(
            tz="US/Eastern"
        )
        self.df["Week"] = self.df["Date"].dt.isocalendar().week
        self.df["DayOfWeek"] = self.df["Date"].dt.dayofweek
        self.df["Date"] = self.df["Date"].dt.date
        self.df["Visitor"] = self.df["Visitor/Neutral"].map(abbreviate_team)
        self.df["Home"] = self.df["Home/Neutral"].map(abbreviate_team)
        cols = ["Date", "Week", "DayOfWeek", "Start (ET)", "Visitor", "Home"]
        self.df = self.df[cols]
        return self.df

    def transform_data(self):
        self.df["Matchup"] = self.df.apply(
            lambda x: x["Visitor"] + "@" + x["Home"], axis=1
        )
        home = self.df.rename(columns={"Home": "Team", "Visitor": "Opponent"})
        home["Side"] = "Home"
        visitor = self.df.rename(columns={"Visitor": "Team", "Home": "Opponent"})
        visitor["Side"] = "Visitor"
        self.df = concat([home, visitor])
        return self.df

    def export_data(self) -> DataFrame:
        self.df.to_csv(self.file_path)
        return self.df

    def read_data(self) -> DataFrame:
        self.df = read_csv(self.file_path, index_col=[0])
        return self.df

    def get_data(self, year: int, months: list[str]) -> DataFrame:
        if os.path.isfile(self.file_path):
            logging.info(f"Reading data from: {self.file_path}")
            self.df = self.read_data()
            self.df["Date"] = to_datetime(self.df["Date"]).dt.date
            return self.df

        logging.info("No existing Schedule dataset found. Fetching data...")
        self.fetch_data(year=year, months=months)
        self.clean_data()
        self.transform_data()
        self.export_data()
        return self.df


def abbreviate_team(team: str) -> str:
    return TEAMS[team]


def main_schedule(debug: bool = False):
    logging.basicConfig(level=logging.WARNING)
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    schedule = ScheduleDataGetter(file_path=f"data/schedule/schedule_{DATESTAMP}.csv")
    schedule.get_data(year=YEAR, months=MONTHS)
    return schedule.df


if __name__ == "__main__":
    main_schedule(True)
