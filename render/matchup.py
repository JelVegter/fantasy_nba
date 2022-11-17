import streamlit as st
from render.tables import filter_player_stat_table_colums, filter_table
from src.league import FANTASY_TEAMS, FANTASY_TEAMS_CURRENT_POINTS
from common.datasets import DATASETS


def app():

    with st.sidebar:
        # Fantasy roster
        fantasy_roster_1 = st.sidebar.selectbox(
            label="Select Fantasy Team", options=FANTASY_TEAMS, index=6
        )
        fantasy_roster_2 = st.sidebar.selectbox(
            label="Select Fantasy Team", options=FANTASY_TEAMS
        )

        # Show Players, Injured Players
        a, b = st.columns(2)
        injury = a.multiselect(
            label="Injured Players", options=["ACTIVE", "DAY_TO_DAY", "OUT"]
        )
        week = b.selectbox(label="Week", options=["This Week", "Next Week"])

        if week == "This Week":
            week = "ThisWeek"
        elif week == "Next Week":
            week = "NextWeek"
        else:
            raise Exception("Invalid week selected")

    st.title("Matchup")
    filters = {}
    if injury:
        filters["Status"] = injury

    c, d = st.columns(2)
    c.title(fantasy_roster_1)
    players_roster_1 = filter_table(DATASETS.roster_players, filters)
    players_roster_1 = players_roster_1.loc[
        players_roster_1["Roster"] == fantasy_roster_1
    ]
    players_roster_1 = filter_player_stat_table_colums(players_roster_1)
    c.dataframe(players_roster_1, height=400, width=1050)
    matchup_points = players_roster_1[week].sum()
    c.write(f"Project Points for {fantasy_roster_1}: {matchup_points}")
    # c.write(FANTASY_TEAMS_CURRENT_POINTS[fantasy_roster_1])

    d.title(fantasy_roster_2)
    players_roster_2 = filter_table(DATASETS.roster_players, filters)
    players_roster_2 = players_roster_2.loc[
        players_roster_2["Roster"] == fantasy_roster_2
    ]
    players_roster_2 = filter_player_stat_table_colums(players_roster_2)
    d.dataframe(players_roster_2, height=400, width=1050)
    matchup_points = players_roster_2[week].sum()
    d.write(f"Project Points for {fantasy_roster_2}: {matchup_points}")
    # d.write(FANTASY_TEAMS_CURRENT_POINTS[fantasy_roster_2])
