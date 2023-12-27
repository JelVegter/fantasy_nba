import streamlit as st
from src.common.utils import fetch_data
from src.common.constants import FANTASY_ROSTERS, CURRENTDAYOFYEAR
from data.db import DB_URI
import polars as pl
from logs import logger


# CURRENTDAYOFYEAR = 291
def retain_latest_per_player(df: pl.DataFrame) -> pl.DataFrame: # TODO
    """
    Retains the latest record for each player based on day_of_year.
    """
    print("Retaining")
    df = df.sort("date", descending=True).groupby("name").agg(pl.first("*"))
    print(len(df))

    return df


def get_all_players() -> pl.DataFrame:
    query = "SELECT * FROM proj_player_points"
    df = fetch_data(query=query, db_uri=DB_URI)
    logger.debug(f"Fetched Data: {query}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")
    return df


def apply_filters(df: pl.DataFrame, filters) -> pl.DataFrame:
    """Apply filters to the DataFrame."""
    for column, values in filters.items():
        if column not in df.columns:
            raise ValueError(
                f"Column {column} does not exist in the DataFrame: {df.columns}."
            )
        if values:
            df = df.filter(df[column].is_in(values))
    return df


def log_filters(**filters) -> None:
    """Log applied filters."""
    logger.debug("-" * 25)
    for key, value in filters.items():
        logger.debug(f"{key}: {value}")
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



def app():
    df_all_players = get_all_players()
    # Free Agents
    df_fa = df_all_players.filter(df_all_players["is_free_agent"] == 1)
    # Roster Players
    df_rp = df_all_players.filter(df_all_players["is_free_agent"] == 0)

    with st.sidebar:
        fantasy_roster_name = st.selectbox("Fantasy Roster", FANTASY_ROSTERS, index=4)
        injury_status = st.multiselect(
            "Injury Status",
            ["ACTIVE", "DAY_TO_DAY", "OUT"],
            default=["ACTIVE", "DAY_TO_DAY"],
        )
        free_agent = st.multiselect("Free Agents", df_fa["name"].unique().to_list())
        teams = st.multiselect("Teams", df_fa["team_abbrev"].unique().to_list())
        position = st.multiselect("Position", df_fa["position"].unique().to_list())
        min_offset, max_offset = st.slider("Day Offset", 0, 6, (0, 6))

    # e, f = st.columns(2)
    e = st.columns(1)[0]
    f = st.columns(1)[0]
    e.title("Free Agents")
    f.title(f"{fantasy_roster_name}")
    filters_fa = {
        "team_abbrev": teams,
        "name": free_agent,
        "position": position,
        "injury_status": injury_status,
        "day_of_year": range(
            CURRENTDAYOFYEAR + min_offset, CURRENTDAYOFYEAR + max_offset + 1
        ),
    }
    filters_roster = {
        "fantasy_roster_name": [fantasy_roster_name],
        "position": position,
        "day_of_year": range(
            CURRENTDAYOFYEAR + min_offset, CURRENTDAYOFYEAR + max_offset + 1
        ),
    }
    df_fa_single = retain_latest_per_player(df_fa)
    df_fa = apply_filters(df_fa, filters_fa)
    df_fa = aggregate_data(df_fa)
    df_fa_combined = df_fa_single.join(df_fa, on="name", how="left")

    print("Fantasy Roster")

    # df_rp_single = retain_latest_per_player(df_rp)
    # df_rp = apply_filters(df_rp, filters_roster)
    df_rp = apply_filters(df_rp, filters_roster)
    df_rp = aggregate_data(df_rp)
    # df_rp_combined = df_rp_single.join(df_rp, on="name", how="left")

    e.dataframe(df_fa_combined.to_pandas(), height=200, width=1000)
    # f.dataframe(df_rp_combined.to_pandas(), height=400, width=1000)
    f.dataframe(df_rp.to_pandas(), height=400, width=1000)
    log_filters(**filters_fa)
    log_filters(**filters_roster)
