import streamlit as st
from src.common.utils import fetch_data
from src.common.constants import FANTASY_ROSTERS, CURRENTDAYOFYEAR, PLAYER_POINTS_COLS
from data.db import DB_URI
import polars as pl
from logs import logger
import json

from dataclasses import dataclass


@dataclass
class FilterOptions:
    player_names: list[str] = None
    team_abbrevs: list[str] = None
    positions: list[str] = None


@dataclass
class Filters:
    fantasy_roster_1_name: str = None
    fantasy_roster_2_name: str = None
    injury_status: list = None
    free_agent: list = None
    teams: list = None
    position: list = None
    day_offset: tuple = (0, 6)


@st.cache_data
def get_player_projections() -> pl.DataFrame:
    query = "SELECT * FROM proj_player_points"
    df = fetch_data(query=query, db_uri=DB_URI)
    logger.debug(f"Fetched Data: {query}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")
    return df


@st.cache_data
def get_players_base() -> pl.DataFrame:
    query = "SELECT * FROM player"
    df = fetch_data(query=query, db_uri=DB_URI)
    logger.debug(f"Fetched Data: {query}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")
    return df


def apply_roster_1_filters(df: pl.DataFrame, filters: Filters) -> pl.DataFrame:
    """Apply filters to the DataFrame based on Filters instance."""
    if filters.fantasy_roster_1_name:
        df = df.filter(pl.col("fantasy_roster_name") == filters.fantasy_roster_1_name)
    if filters.injury_status:
        df = df.filter(pl.col("injury_status").is_in(filters.injury_status))
    return df


def apply_roster_2_filters(df: pl.DataFrame, filters: Filters) -> pl.DataFrame:
    """Apply filters to the DataFrame based on Filters instance."""
    if filters.fantasy_roster_2_name:
        df = df.filter(pl.col("fantasy_roster_name") == filters.fantasy_roster_2_name)
    if filters.injury_status:
        df = df.filter(pl.col("injury_status").is_in(filters.injury_status))
    return df


def log_filters(**filters) -> None:
    """Log applied filters."""
    logger.debug("-" * 25)
    for key, value in filters.items():
        logger.debug(f"{key}: {value}")

    logger.info(json.dumps(filters, indent=4))
    print(json.dumps(filters, indent=4))
    logger.debug("-" * 25)


def aggregate_data(df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate data for players."""
    df = (
        df.select(
            "name",
            "avg_points",
            "projected_avg_points",
        )
        .group_by(["name"])
        .agg(
            [
                pl.count().alias("games"),
                pl.col("avg_points").sum().alias("sum_avg_points"),
                pl.col("projected_avg_points").sum().alias("sum_proj_avg_points"),
            ]
        )
    )
    return df.sort(by="sum_avg_points", descending=True)


def filter_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """Filter columns in the DataFrame."""
    return df.select(columns)


def setup_sidebar(df_base: pl.DataFrame) -> Filters:
    """Setup Streamlit sidebar for filtering and return a Filters instance."""

    if "filters" not in st.session_state:
        st.session_state.filters = Filters()

    if "filter_options" not in st.session_state:
        st.session_state.filter_options = FilterOptions(
            player_names=df_base["name"].unique().to_list(),
            team_abbrevs=df_base["team_abbrev"].unique().to_list(),
            positions=df_base["position"].unique().to_list(),
        )

    fantasy_roster_1_index = 4 if len(FANTASY_ROSTERS) > 5 else 0
    fantasy_roster_1_name = st.sidebar.selectbox(
        "Fantasy Roster 1",
        FANTASY_ROSTERS,
        index=fantasy_roster_1_index,
        key="fantasy_roster_name",
    )
    fantasy_roster_2_index = 4 if len(FANTASY_ROSTERS) > 5 else 0
    fantasy_roster_2_name = st.sidebar.selectbox(
        "Fantasy Roster 2",
        FANTASY_ROSTERS,
        index=fantasy_roster_2_index,
        key="fantasy_roster_2_name",
    )
    injury_status = st.sidebar.multiselect(
        "Injury Status",
        ["ACTIVE", "DAY_TO_DAY", "OUT"],
        default=["ACTIVE"],
        key="injury_status",
    )

    day_offset = st.sidebar.slider("Day Offset", 0, 6, (0, 6), key="day_offset")

    return Filters(
        fantasy_roster_1_name,
        fantasy_roster_2_name,
        injury_status,
        day_offset,
    )


def app():
    df_projections = get_player_projections()
    df_base = get_players_base()
    filters = setup_sidebar(df_base)

    # Calculate projections per player for games, filtered by a date range

    # Aggregate projections
    df_projections = df_projections.filter(
        pl.col("day_of_year").is_in(
            range(
                CURRENTDAYOFYEAR + filters.day_offset[0],
                CURRENTDAYOFYEAR + filters.day_offset[1] + 1,
            )
        )
    )
    df_rojections_agg = aggregate_data(df_projections)

    # Filter the free agent and roster DataFrames, then add the aggregated projections
    df_roster_player_1 = apply_roster_1_filters(df_base, filters)
    df_roster_player_1 = df_roster_player_1.join(
        df_rojections_agg, on="name", how="left"
    )

    df_roster_player_2 = apply_roster_2_filters(df_base, filters)
    df_roster_player_2 = df_roster_player_2.join(
        df_rojections_agg, on="name", how="left"
    )

    e = st.columns(1)[0]
    e.title(filters.fantasy_roster_1_name)
    df_roster_player_1 = filter_columns(
        df_roster_player_1,
        PLAYER_POINTS_COLS,
    )
    # Render Dataframe
    e.dataframe(df_roster_player_1.to_pandas(), height=400, width=1000)

    # Sum the polars dataframe avg_points column

    st.markdown(int(df_roster_player_1["sum_avg_points"].sum()))

    f = st.columns(1)[0]
    f.title(f"{filters.fantasy_roster_2_name}")
    df_roster_player_2 = filter_columns(
        df_roster_player_2,
        PLAYER_POINTS_COLS,
    )
    # Render Dataframe
    f.dataframe(df_roster_player_2.to_pandas(), height=400, width=1000)
    st.markdown(int(df_roster_player_2["sum_avg_points"].sum()))
