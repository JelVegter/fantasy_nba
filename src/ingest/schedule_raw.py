import asyncio
import aiohttp
from pandas import DataFrame, read_html, concat, to_datetime
from enum import Enum
from pytz import timezone

TIMEZONE = timezone("US/Eastern")


class TeamEnum(Enum):
    ATL = "Atlanta Hawks"
    BOS = "Boston Celtics"
    BKN = "Brooklyn Nets"
    CHA = "Charlotte Hornets"
    CHI = "Chicago Bulls"
    CLE = "Cleveland Cavaliers"
    DAL = "Dallas Mavericks"
    DEN = "Denver Nuggets"
    DET = "Detroit Pistons"
    GSW = "Golden State Warriors"
    HOU = "Houston Rockets"
    IND = "Indiana Pacers"
    LAL = "Los Angeles Lakers"
    LAC = "Los Angeles Clippers"
    MEM = "Memphis Grizzlies"
    MIA = "Miami Heat"
    MIL = "Milwaukee Bucks"
    MIN = "Minnesota Timberwolves"
    NOP = "New Orleans Pelicans"
    NYK = "New York Knicks"
    OKC = "Oklahoma City Thunder"
    ORL = "Orlando Magic"
    PHL = "Philadelphia 76ers"
    PHO = "Phoenix Suns"
    POR = "Portland Trail Blazers"
    SAC = "Sacramento Kings"
    SAS = "San Antonio Spurs"
    TOR = "Toronto Raptors"
    UTA = "Utah Jazz"
    WAS = "Washington Wizards"


async def fetch(session, url: str) -> str:
    async with session.get(url, ssl=False) as response:
        return await response.text()


async def fetch_api_data(urls: list) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def convert_to_24_hour_format(time_str: str) -> str:
    if time_str.endswith("p"):
        hour, minute = map(int, time_str[:-1].split(":"))
        if hour != 12:  # If it's 12 PM, we don't need to add 12
            hour += 12
        return f"{hour:02}:{minute:02}"
    elif time_str.endswith("a"):
        hour, minute = map(int, time_str[:-1].split(":"))
        if hour == 12:  # If it's 12 AM, hour becomes 0
            hour = 0
        return f"{hour:02}:{minute:02}"
    else:
        # Return original string if it doesn't end with 'a' or 'p'
        return time_str


class ScheduleGetter:
    async def fetch_data(self, year: int) -> DataFrame:  # Note the 'async' keyword here
        months = [
            "october",
            "november",
            "december",
            "january",
            "february",
            "march",
            "april",
        ]
        base_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"
        urls = [base_url.format(year, month) for month in months]
        html_tables = [
            read_html(content)[0] if content else None
            for content in await fetch_api_data(urls)
        ]
        self.df = concat([table for table in html_tables if table is not None])
        return self.df

    def clean_data(self) -> DataFrame:
        self.df.columns = self.df.columns.str.lower()
        # Convert time to 24-hour format
        self.df["time"] = self.df["start (et)"].apply(convert_to_24_hour_format)
        self.df["date"] = to_datetime(self.df["date"], errors="coerce").dt.tz_localize(
            tz=TIMEZONE
        )
        self.df["datetime"] = to_datetime(
            self.df["date"].astype(str) + " " + self.df["time"]
        )
        self.df["week"] = self.df["date"].dt.isocalendar().week
        self.df["day_of_year"] = self.df["date"].dt.dayofyear
        self.df["day_of_week"] = self.df["date"].dt.dayofweek
        self.df["date"] = self.df["date"].dt.date
        self.df["visitor"] = self.df["visitor/neutral"].map(abbreviate_team)
        self.df["home"] = self.df["home/neutral"].map(abbreviate_team)
        return self.df

    def transform_data(self) -> DataFrame:
        # Prepare the matchup column
        self.df["matchup"] = self.df.apply(
            lambda x: x["visitor"] + "@" + x["home"], axis=1
        )

        # Split the data into home and visitor dataframes
        home = self.df.rename(columns={"home": "team", "visitor": "opponent"}).copy()
        home["is_visitor"] = 0  # 'home' indication

        visitor = self.df.rename(columns={"visitor": "team", "home": "opponent"}).copy()
        visitor["is_visitor"] = 1  # 'visitor' indication

        # Concatenate the home and visitor dataframes
        self.df = concat([home, visitor])

        # Select only the columns that match the Schedule model attributes
        # required_columns = [
        #     "date",
        #     "week",
        #     "day_of_week",
        #     "day_of_year",
        #     "time",
        #     "opponent",
        #     "team",
        #     "matchup",
        #     "is_visitor",
        # ]
        # self.df = self.df[required_columns]

        return self.df

    async def process_data(self, year: int) -> DataFrame:
        await self.fetch_data(year=year)
        self.clean_data()
        self.transform_data()
        return self.df


def abbreviate_team(team: str) -> str:
    teams = {e.value: e.name for e in TeamEnum}
    return teams.get(team, team)


async def main():
    schedule = ScheduleGetter()
    df = await schedule.process_data(year=2024)
    df.to_csv("schedule.csv", index=False)
    print(df)


if __name__ == "__main__":
    asyncio.run(main())
