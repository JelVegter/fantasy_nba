import logging
import streamlit as st
from src.league import FANTASY_TEAMS, league
from render.tables import (
    format_week_schedule_table,
    filter_table,
    filter_player_stat_table_colums,
)
from common.datasets import DATASETS
from common.datetime_utils import CURRENTWEEKNUMBER, NEXTWEEKNUMBER
from common.constants import TEAMS


def app():

    with st.sidebar:
        # Fantasy roster
        fantasy_roster = st.sidebar.selectbox(
            label="Select Fantasy Team", options=FANTASY_TEAMS, index=6
        )

        # Show Players, Injured Players
        a, b = st.columns(2)
        nr_of_rows = a.number_input(
            "Show Players", format="%i", min_value=20, max_value=50, step=10
        )
        injury = b.multiselect(
            label="Injured Players", options=["ACTIVE", "DAY_TO_DAY", "OUT"]
        )

        # Filter Player, Filter Teams
        c, d = st.columns(2)
        teams = d.multiselect(label="Filter Teams", options=TEAMS.values())
        free_agents = [fa.name for fa in league.free_agents()]
        free_agent = c.multiselect(label="Filter Players", options=free_agents)

        # Period
        e, f = st.columns(2)
        positions = set([fa.position for fa in league.free_agents()])
        position = e.multiselect(label="Position", options=positions)

        week_numbers = [_ for _ in range(1, 52)]
        week = f.selectbox(
            label="Week", options=["This Week", "Next Week"] + week_numbers
        )
        if week == "This Week":
            week = CURRENTWEEKNUMBER
        elif week == "Next Week":
            week = NEXTWEEKNUMBER
        else:
            week = int(week)

    st.title("Schedule")
    filters = {}
    if week:
        filters["Week"] = week

    if teams:
        filters["Team"] = teams

    week_schedule = filter_table(DATASETS.week_vw, filters)
    week_schedule = format_week_schedule_table(week_schedule)
    st.dataframe(week_schedule, height=400, width=1050)

    e, f = st.columns(2)
    e.title("Free Agents")
    filters = {}
    if teams:
        filters["Team"] = teams

    if free_agent:
        filters["Player"] = free_agent

    if position:
        filters["Position"] = position

    if injury:
        filters["Status"] = injury

    free_agents = filter_table(DATASETS.free_agents, filters, nr_of_rows)
    free_agents = filter_player_stat_table_colums(free_agents)
    e.dataframe(free_agents, height=400)

    f.title("Roster Players")
    filters = {}
    if fantasy_roster:
        filters["Roster"] = fantasy_roster

    roster_players = filter_table(DATASETS.roster_players, filters)
    roster_players = filter_player_stat_table_colums(roster_players)
    f.dataframe(roster_players, height=400)