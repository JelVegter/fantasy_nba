import asyncio
import json
import aiohttp
from pandas import DataFrame, concat, to_datetime
from src.espn.league import YEAR
from data.db import Session
from src.common.constants import TIMEZONE
from models.schedule import Schedule


async def fetch(session, url: str) -> str:
    async with session.get(url, ssl=False) as response:
        return await response.text()


async def fetch_api_data(urls: list) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


NBA_SCHEDULE_URL = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"


async def fetch_nba_schedule_json() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            NBA_SCHEDULE_URL,
            timeout=60,
            ssl=False,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            },
        ) as resp:
            resp.raise_for_status()
            text = await resp.text()
            try:
                return json.loads(text)
            except Exception:
                # Attempt to recover if there is leading noise/BOM
                start = text.find("{")
                if start != -1:
                    return json.loads(text[start:])
                raise


def normalize_tricode(code: str) -> str:
    mapping = {
        "PHI": "PHL",  # TeamEnum uses PHL
        "PHX": "PHO",  # TeamEnum uses PHO
    }
    return mapping.get(code, code)


class ScheduleGetter:
    async def fetch_data(self, year: int) -> DataFrame:  # Note the 'async' keyword here
        raw = await fetch_nba_schedule_json()
        rows = []
        game_dates = raw.get("leagueSchedule", {}).get("gameDates", [])
        for gd in game_dates:
            for g in gd.get("games", []):
                dt_utc = g.get("gameDateTimeUTC")
                if not dt_utc:
                    continue
                dt = to_datetime(dt_utc, utc=True).tz_convert(TIMEZONE)

                # Season window similar to previous (Oct–Jun across two calendar years)
                if not (
                    (dt.year == year - 1 and dt.month >= 10)
                    or (dt.year == year and dt.month <= 6)
                ):
                    continue

                home = normalize_tricode(g["homeTeam"]["teamTricode"])
                away = normalize_tricode(g["awayTeam"]["teamTricode"])
                rows.append(
                    {
                        "date": dt,  # tz-aware datetime
                        "time": dt.strftime("%H:%M"),
                        "visitor": away,
                        "home": home,
                    }
                )
        self.df = DataFrame(rows)
        return self.df

    def clean_data(self) -> DataFrame:
        # Derive calendar fields from tz-aware datetime
        self.df["week"] = self.df["date"].dt.isocalendar().week
        self.df["day_of_year"] = self.df["date"].dt.dayofyear
        self.df["day_of_week"] = self.df["date"].dt.dayofweek
        self.df["date"] = self.df["date"].dt.date
        # Drop rows with missing teams or time
        self.df = self.df.dropna(subset=["visitor", "home", "time"]).copy()
        return self.df

    def transform_data(self) -> DataFrame:
        # Prepare the matchup column
        self.df["matchup"] = self.df.apply(
            lambda x: (x["visitor"] or "") + "@" + (x["home"] or ""), axis=1
        )

        # Split the data into home and visitor dataframes
        home = self.df.rename(columns={"home": "team", "visitor": "opponent"}).copy()
        home["is_visitor"] = 0  # 'home' indication

        visitor = self.df.rename(columns={"visitor": "team", "home": "opponent"}).copy()
        visitor["is_visitor"] = 1  # 'visitor' indication

        # Concatenate the home and visitor dataframes
        self.df = concat([home, visitor])

        # Select only the columns that match the Schedule model attributes
        required_columns = [
            "date",
            "week",
            "day_of_week",
            "day_of_year",
            "time",
            "opponent",
            "team",
            "matchup",
            "is_visitor",
        ]
        self.df = self.df[required_columns]

        return self.df

    async def process_data(self, year: int) -> DataFrame:
        await self.fetch_data(year=year)
        self.clean_data()
        self.transform_data()
        return self.df


def abbreviate_team(team: str) -> str:
    # No longer used with NBA tricodes; kept for backward compatibility if needed
    return team


async def _ingest_schedule_async() -> None:
    getter = ScheduleGetter()
    df = await getter.process_data(year=YEAR)
    session = Session()
    try:
        session.query(Schedule).delete()
        for index, row in df.iterrows():
            schedule_row = Schedule(
                date=row["date"],
                day_of_year=row["day_of_year"],
                week=row["week"],
                day_of_week=row["day_of_week"],
                time=row["time"],
                opponent_abbrev=row["opponent"],
                team_abbrev=row["team"],
                matchup=row["matchup"],
                is_visitor=row["is_visitor"],
            )
            session.merge(schedule_row)
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()


def ingest_schedule() -> None:
    asyncio.run(_ingest_schedule_async())


if __name__ == "__main__":
    ingest_schedule()
