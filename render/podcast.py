import streamlit as st
from src.common.utils import fetch_data
from src.common.constants import FANTASY_ROSTERS, CURRENTDAYOFYEAR, PLAYER_POINTS_COLS
from data.db import DB_URI
import polars as pl
from logs import logger
import json
from typing import Optional
import os

from dataclasses import dataclass
from youtube_transcript_api import YouTubeTranscriptApi
from llm import extract_player_mentions, process_video, PROCESSED_VIDEOS_PATH

FANTASY_ROSTER_INDEX = 6 if len(FANTASY_ROSTERS) > 5 else 0


@dataclass
class FilterOptions:
    player_names: list[str] = None
    team_abbrevs: list[str] = None
    positions: list[str] = None


@dataclass
class Filters:
    fantasy_roster_name: str = None
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


def fetch_transcript(video_id: str) -> str:
    """Fetches the transcript for a given YouTube video ID."""
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([segment["text"] for segment in transcript_data])
        return transcript
    except Exception as e:
        logger.error(f"Failed to retrieve transcript for video {video_id}: {e}")
        return ""


def get_processed_videos() -> list[str]:
    """Get a list of previously processed video IDs."""
    video_files = [f for f in os.listdir(PROCESSED_VIDEOS_PATH) if f.endswith(".json")]
    return [f.replace(".json", "") for f in video_files]


def process_youtube_videos(
    video_urls: list, players: Optional[list[dict]]
) -> pl.DataFrame:
    """
    Process a list of YouTube URLs to extract player mentions.
    """
    mentioned_players = []

    for url in video_urls:
        video_id = url.split("v=")[-1]
        video_id = video_id.split("&")[0]
        mentioned_players.extend(process_video(video_id, players))

    return pl.DataFrame(mentioned_players)


def apply_fa_filters(df: pl.DataFrame, filters: Filters) -> pl.DataFrame:
    """Apply filters to the DataFrame based on Filters instance."""
    df = df.filter(df["is_free_agent"] == 1)
    if filters.teams:
        df = df.filter(pl.col("team_abbrev").is_in(filters.teams))
    if filters.position:
        df = df.filter(pl.col("position").is_in(filters.position))
    if filters.free_agent:
        df = df.filter(pl.col("name").is_in(filters.free_agent))
    if filters.injury_status:
        df = df.filter(pl.col("injury_status").is_in(filters.injury_status))
    return df


def apply_roster_filters(df: pl.DataFrame, filters: Filters) -> pl.DataFrame:
    """Apply filters to the DataFrame based on Filters instance."""
    df = df.filter(df["is_free_agent"] == 0)
    if filters.fantasy_roster_name:
        df = df.filter(pl.col("fantasy_roster_name") == filters.fantasy_roster_name)
    if filters.injury_status:
        df = df.filter(pl.col("injury_status").is_in(filters.injury_status))
    return df


def log_filters(**filters) -> None:
    """Log applied filters."""
    logger.debug("-" * 25)
    for key, value in filters.items():
        logger.debug(f"{key}: {value}")
    logger.info(json.dumps(filters, indent=4))
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


def setup_sidebar(df: pl.DataFrame) -> Filters:
    """Setup Streamlit sidebar for filtering and return a Filters instance."""

    if "filters" not in st.session_state:
        st.session_state.filters = Filters()

    if "filter_options" not in st.session_state:
        st.session_state.filter_options = FilterOptions(
            player_names=df["name"].unique().to_list(),
            team_abbrevs=df["team_abbrev"].unique().to_list(),
            positions=df["position"].unique().to_list(),
        )

    # Add video selection
    processed_videos = get_processed_videos()
    selected_videos = st.sidebar.multiselect(
        "Select Previously Processed Videos",
        processed_videos,
        default=[processed_videos[0]] if processed_videos else None,
        format_func=lambda x: f"Video: {x}",
    )

    # Keep the URL input for new videos
    new_video_urls = st.sidebar.text_area(
        "Or Enter New YouTube URLs (one per line)"
    ).splitlines()

    fantasy_roster_name = st.sidebar.selectbox(
        "Fantasy Roster",
        FANTASY_ROSTERS,
        index=FANTASY_ROSTER_INDEX,
        key="fantasy_roster_name",
    )
    injury_status = st.sidebar.multiselect(
        "Injury Status",
        ["ACTIVE", "DAY_TO_DAY", "OUT"],
        default=["ACTIVE", "DAY_TO_DAY"],
        key="injury_status",
    )

    free_agent = st.sidebar.multiselect(
        "Free Agents",
        st.session_state.filter_options.player_names,
        default=st.session_state.filters.free_agent,
        key="free_agent",
    )

    teams = st.sidebar.multiselect(
        "Teams",
        st.session_state.filter_options.team_abbrevs,
        default=st.session_state.filters.teams,
        key="teams",
    )

    position = st.sidebar.multiselect(
        "Position",
        st.session_state.filter_options.positions,
        default=st.session_state.filters.position,
        key="position",
    )

    day_offset = st.sidebar.slider("Day Offset", 0, 6, (0, 6), key="day_offset")

    # Store selected videos in session state
    st.session_state.selected_videos = selected_videos
    st.session_state.new_video_urls = new_video_urls

    return Filters(
        fantasy_roster_name, injury_status, free_agent, teams, position, day_offset
    )


def app():
    df_projections = get_player_projections()
    df_base = get_players_base()
    filters = setup_sidebar(df_base)

    players = df_base.select(["name", "team_abbrev"]).unique().to_dicts()

    # Process both selected videos and new URLs
    video_urls = []

    # Add URLs for selected processed videos
    if hasattr(st.session_state, "selected_videos"):
        video_urls.extend(
            [
                f"https://www.youtube.com/watch?v={vid}"
                for vid in st.session_state.selected_videos
            ]
        )

    # Add new video URLs
    if hasattr(st.session_state, "new_video_urls"):
        video_urls.extend(st.session_state.new_video_urls)

    # Process videos
    if video_urls:
        logger.info(f"Processing {len(video_urls)} videos")
        for url in video_urls:
            logger.info(f"Processing video {url}")
        player_mentions_df = process_youtube_videos(video_urls, players)
    else:
        st.warning(
            "Please select previously processed videos or enter new YouTube URLs"
        )
        return

    # Calculate projections per player, filtered by a date range
    df_projections = df_projections.filter(
        pl.col("day_of_year").is_in(
            range(
                CURRENTDAYOFYEAR + filters.day_offset[0],
                CURRENTDAYOFYEAR + filters.day_offset[1] + 1,
            )
        )
    )
    df_projections_agg = aggregate_data(df_projections)

    # Get base player data
    df_players = df_base.join(df_projections_agg, on="name", how="left")
    df_players = df_players.with_columns(
        pl.col("fantasy_points").mul(pl.col("games")).alias("sum_fantasy_points")
    )
    df_players = df_players.filter(pl.col("sum_fantasy_points").is_not_null())

    # Join with player mentions to get analysis data
    df_analysis = df_players.join(
        player_mentions_df.select(["name", "advice", "urgency", "analysis"]),
        on="name",
        how="inner",
    )

    # Print players that were mentioned but didn't join
    mentioned_players = set(player_mentions_df["name"].to_list())
    joined_players = set(df_analysis["name"].to_list())
    missing_players = mentioned_players - joined_players

    if missing_players:
        st.warning("Players mentioned but not in database:")
        for player in missing_players:
            st.write(f"- {player}")

    # Reorder columns by creating a new selection with desired order
    analysis_cols = ["name", "advice", "urgency", "analysis", "is_free_agent"]
    remaining_cols = [col for col in PLAYER_POINTS_COLS if col != "name"]
    display_cols = analysis_cols + remaining_cols

    # Display combined analysis and stats
    st.title("Player Analysis")
    if not df_analysis.is_empty():
        # Sort by urgency if present, otherwise by fantasy points
        df_display = df_analysis.sort("urgency", descending=True)

        st.dataframe(
            df_display.select(display_cols).to_pandas(),
            height=400,
            width=1000,
        )
    else:
        st.write("No analyzed players found in free agents pool.")

    # Render Fantasy Roster Table
    st.title(filters.fantasy_roster_name)
    df_roster_player = apply_roster_filters(df_base, filters)
    df_roster_player = df_roster_player.join(df_projections_agg, on="name", how="left")
    # Add the same fantasy points calculation as before
    df_roster_player = df_roster_player.with_columns(
        pl.col("fantasy_points").mul(pl.col("games")).alias("sum_fantasy_points")
    )
    df_roster_player = df_roster_player.filter(
        pl.col("sum_fantasy_points").is_not_null()
    )

    # Join with player mentions to add analysis columns
    df_roster_player = df_roster_player.join(
        player_mentions_df.select(["name", "advice", "urgency"]), on="name", how="left"
    )

    # Reorder columns to put name, advice, urgency first
    roster_display_cols = ["name", "advice", "urgency"] + [
        col for col in PLAYER_POINTS_COLS if col != "name"
    ]

    st.dataframe(
        filter_columns(df_roster_player, roster_display_cols).to_pandas(),
        height=400,
        width=1000,
    )
