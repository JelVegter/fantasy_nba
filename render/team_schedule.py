import streamlit as st
from src.common.utils import fetch_data
from src.common.constants import FANTASY_ROSTERS, day_of_week_to_name
from data.db import DB_URI
import polars as pl
from logs import logger

def get_schedule() -> pl.DataFrame:
    query = "SELECT * FROM schedule ORDER BY day_of_week asc"
    df = fetch_data(query=query, db_uri=DB_URI)
    logger.debug(f"Fetched Data: {query}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")
    return df

def transform_schedule(df: pl.DataFrame) -> pl.DataFrame:
    df = (
        df.select(
            "team_abbrev",
            "week",
            "day_of_week",
            "opponent_abbrev",
        )
        .pivot(
            index=["team_abbrev","week"],
            columns="day_of_week",
            values="opponent_abbrev"
        )
    )
    week_day_cols = ["0","1","2","3","4","5","6"]
    df.columns = [day_of_week_to_name(int(col)) if col in week_day_cols else col for col in df.columns]
    return df

def calculate_games_played(df: pl.DataFrame) -> pl.DataFrame:
    # Debug: Print data types of the DataFrame and DataFrame itself
    print(df.dtypes)
    print(df.columns)
    print(df)

    # List of day columns
    day_columns = [col for col in df.columns if col not in ["team_abbrev", "week"]]

    # Initialize a column for games played with zeros
    df = df.with_columns(pl.lit(0).alias("Games"))

    # Iterate over each day column and increment the Games column for each non-null entry
    for day in day_columns:
        df = df.with_columns((pl.col("Games") + pl.col(day).is_not_null().cast(pl.UInt32)).alias("Games"))

    # Debug: Print the DataFrame after modification
    print(df)

    return df



# def calculate_games_played(df: pl.DataFrame) -> pl.DataFrame:
#     df = df.with_columns(
#         pl.sum([
#             pl.col(day).is_not_null().cast(pl.UInt32) for day in df.columns if day not in ["team_abbrev", "week"]
#         ]).alias("Games")
#     )

#     return df


def app():
    df = get_schedule()
    df = transform_schedule(df)
    df = df.filter(pl.col("week") == 52)
    df = calculate_games_played(df)
    # # Free Agents
    # df_fa = df_all_players.filter(df_all_players["is_free_agent"] == 1)
    # # Roster Players
    # df_rp = df_all_players.filter(df_all_players["is_free_agent"] == 0)

    with st.sidebar:
        fantasy_roster_name = st.selectbox("Fantasy Roster", FANTASY_ROSTERS, index=4)
        injury_status = st.multiselect(
            "Injury Status",
            ["ACTIVE", "DAY_TO_DAY", "OUT"],
            default=["ACTIVE", "DAY_TO_DAY"],
        )
        # free_agent = st.multiselect("Free Agents", df_fa["name"].unique().to_list())
        # teams = st.multiselect("Teams", df_fa["team_abbrev"].unique().to_list())
        # position = st.multiselect("Position", df_fa["position"].unique().to_list())
        # min_offset, max_offset = st.slider("Day Offset", 0, 6, (0, 6))
    
    st.title("Schedule")
    st.dataframe(df.to_pandas(), height=400, width=1000)
    # # e, f = st.columns(2)
    # e = st.columns(1)[0]
    # f = st.columns(1)[0]
    # e.title("Free Agents")
    # f.title(f"{fantasy_roster_name}")
    # filters_fa = {
    #     "team_abbrev": teams,
    #     "name": free_agent,
    #     "position": position,
    #     "injury_status": injury_status,
    #     "day_of_year": range(
    #         CURRENTDAYOFYEAR + min_offset, CURRENTDAYOFYEAR + max_offset + 1
    #     ),
    # }
    # filters_roster = {
    #     "fantasy_roster_name": [fantasy_roster_name],
    #     "position": position,
    #     "day_of_year": range(
    #         CURRENTDAYOFYEAR + min_offset, CURRENTDAYOFYEAR + max_offset + 1
    #     ),
    # }
    # df_fa_single = retain_latest_per_player(df_fa)
    # df_fa = apply_filters(df_fa, filters_fa)
    # df_fa = aggregate_data(df_fa)
    # df_fa_combined = df_fa_single.join(df_fa, on="name", how="left")

    # print("Fantasy Roster")

    # # df_rp_single = retain_latest_per_player(df_rp)
    # # df_rp = apply_filters(df_rp, filters_roster)
    # df_rp = apply_filters(df_rp, filters_roster)
    # df_rp = aggregate_data(df_rp)
    # # df_rp_combined = df_rp_single.join(df_rp, on="name", how="left")

    # e.dataframe(df_fa_combined.to_pandas(), height=200, width=1000)
    # # f.dataframe(df_rp_combined.to_pandas(), height=400, width=1000)
    # f.dataframe(df_rp.to_pandas(), height=400, width=1000)
    # log_filters(**filters_fa)
    # log_filters(**filters_roster)
