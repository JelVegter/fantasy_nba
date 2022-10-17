import asyncio
import aiohttp
import requests
from pandas import DataFrame, read_html, concat, to_datetime

import logging
from logging.config import fileConfig

from common.datetime_utils import DATESTAMP
from common.constants import MONTHS, TEAMS
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


def fetch_game_schedule(year: int, months: list[str]) -> DataFrame:
    base_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"
    urls = [base_url.format(year, month) for month in months]
    urls_content = [requests.get(url).content for url in urls]

    html_tables = []
    for i, content in enumerate(urls_content):
        try:
            html_tables.append(read_html(content)[0])
        except Exception as e:
            logging.warning(f"{e} - {urls[i]}")

    schedule = concat(html_tables)
    logging.debug(schedule)
    return schedule


def clean_game_schedule(df: DataFrame) -> DataFrame:
    df["Date"] = to_datetime(df["Date"], errors="coerce").dt.tz_localize(
        tz="US/Eastern"
    )
    df["Week"] = df["Date"].dt.isocalendar().week
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["Visitor"] = df["Visitor/Neutral"].map(abbreviate_team)
    df["Home"] = df["Home/Neutral"].map(abbreviate_team)
    cols = ["Date", "Week", "DayOfWeek", "Start (ET)", "Visitor", "Home"]
    df = df[cols]
    logging.debug(df)
    return df


def transform_game_schedule(df: DataFrame) -> DataFrame:
    df["Matchup"] = df.apply(lambda x: x["Visitor"] + "@" + x["Home"], axis=1)
    home = df.rename(columns={"Home": "Team", "Visitor": "Opponent"})
    home["Side"] = "Home"
    visitor = df.rename(columns={"Visitor": "Team", "Home": "Opponent"})
    visitor["Side"] = "Visitor"
    return concat([home, visitor])


def export_game_schedule(df: DataFrame) -> DataFrame:
    df.to_csv(f"data/schedule/schedule_{DATESTAMP}.csv")
    return df


def abbreviate_team(team: str) -> str:
    return TEAMS[team]


def main_schedule(debug: bool = False):
    logging.basicConfig(level=logging.WARNING)
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    df = fetch_game_schedule(YEAR, MONTHS)
    df = clean_game_schedule(df)
    df = transform_game_schedule(df)
    export_game_schedule(df)
    return df


if __name__ == "__main__":
    main_schedule(True)
