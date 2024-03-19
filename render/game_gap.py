import streamlit as st
from src.common.utils import fetch_data
from src.common.constants import FANTASY_ROSTERS, day_of_week_to_name, CURRENTWEEKNUMBER
from data.db import DB_URI
import polars as pl
from logs import logger


def highlight_non_null(s):
    """
    Highlight non-null cells in a DataFrame
    """
    return ["background-color: green" if v is not None else "" for v in s]


def get_schedule() -> pl.DataFrame:
    query = "SELECT * FROM schedule ORDER BY day_of_week asc"
    df = fetch_data(query=query, db_uri=DB_URI)
    logger.debug(f"Fetched Data: {query}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")
    return df


def calculate_no_game_days_pl(df: pl.DataFrame) -> pl.DataFrame:
    # Ensure DataFrame is sorted by team and date
    df = df.sort(["team_abbrev", "date"])

    # Add a column for the next game date per team
    df = df.with_columns(
        pl.col("date").shift(-1).over("team_abbrev").alias("next_game_date")
    )

    # Calculate the difference in days to the next game
    df = df.with_columns(
        (pl.col("next_game_date") - pl.col("date")).dt.days().alias("days_to_next_game")
    )

    # Calculate no-game days following. If the team plays the next day, this will be 0.
    # Otherwise, it's the days to the next game minus 1, taking care of negative values as well.
    df = df.with_columns(
        pl.when(pl.col("days_to_next_game") > 1)
        .then(pl.col("days_to_next_game") - 1)
        .otherwise(0)
        .alias("no_game_days_following")
    )

    # Drop the intermediate calculation columns
    df = df.drop(["next_game_date", "days_to_next_game"])

    df = df.filter(pl.col("team_abbrev") == "ATL")
    print(df)
    df = df.filter(pl.col("week") == 12)  # TODO

    return df


def transform_schedule(df: pl.DataFrame) -> pl.DataFrame:
    df = df.select(
        "team_abbrev",
        "week",
        "day_of_week",
        "no_game_days_following",
    ).pivot(
        index=["team_abbrev", "week"],
        columns="day_of_week",
        values="no_game_days_following",
    )
    week_day_cols = ["0", "1", "2", "3", "4", "5", "6"]
    desired_column_order = ["team_abbrev", "week"] + week_day_cols
    df = df.select(desired_column_order)

    df.columns = [
        day_of_week_to_name(int(col)) if col in week_day_cols else col
        for col in df.columns
    ]
    return df


def app():
    df = get_schedule()
    df = calculate_no_game_days_pl(df)
    st.dataframe(
        df.to_pandas().style.apply(highlight_non_null, axis=0), height=400, width=1000
    )
    df = transform_schedule(df)
    st.dataframe(
        df.to_pandas().style.apply(highlight_non_null, axis=0), height=400, width=1000
    )

    with st.sidebar:
        fantasy_roster_name = st.selectbox("Fantasy Roster", FANTASY_ROSTERS, index=4)
        injury_status = st.multiselect(
            "Injury Status",
            ["ACTIVE", "DAY_TO_DAY", "OUT"],
            default=["ACTIVE", "DAY_TO_DAY"],
        )
        week = st.selectbox("Week", list(range(1, 52)), CURRENTWEEKNUMBER - 1)

    df = df.filter(pl.col("week") == week)
    print(df)
    st.title("Game Gap")
    st.dataframe(
        df.to_pandas().style.apply(highlight_non_null, axis=0), height=400, width=1000
    )
