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


def transform_schedule(df: pl.DataFrame) -> pl.DataFrame:
    df = df.select(
        "team_abbrev",
        "week",
        "day_of_week",
        "opponent_abbrev",
    ).pivot(
        index=["team_abbrev", "week"], columns="day_of_week", values="opponent_abbrev"
    )
    week_day_cols = ["0", "1", "2", "3", "4", "5", "6"]
    df.columns = [
        day_of_week_to_name(int(col)) if col in week_day_cols else col
        for col in df.columns
    ]
    return df


def calculate_games_played(df: pl.DataFrame) -> pl.DataFrame:
    # List of day columns
    day_columns = [col for col in df.columns if col not in ["team_abbrev", "week"]]

    # Initialize a column for games played with zeros
    df = df.with_columns(pl.lit(0).alias("Games"))

    # Iterate over each day column and increment the Games column for each non-null entry
    for day in day_columns:
        df = df.with_columns(
            (pl.col("Games") + pl.col(day).is_not_null().cast(pl.UInt32)).alias("Games")
        )

    return df


def app():
    df = get_schedule()
    df = transform_schedule(df)

    with st.sidebar:
        fantasy_roster_name = st.selectbox("Fantasy Roster", FANTASY_ROSTERS, index=4)
        injury_status = st.multiselect(
            "Injury Status",
            ["ACTIVE", "DAY_TO_DAY", "OUT"],
            default=["ACTIVE", "DAY_TO_DAY"],
        )
        week = st.selectbox("Week", list(range(1, 52)), CURRENTWEEKNUMBER - 1)

    df = df.filter(pl.col("week") == week)
    df = calculate_games_played(df)
    st.title("Schedule")
    logger.debug("-" * 25)
    logger.debug(df.head())
    styled_df = df.to_pandas().style.apply(highlight_non_null, axis=0)
    st.dataframe(styled_df, height=400, width=1000)
