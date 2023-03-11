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
        position = e.multiselect(label="position", options=positions)

        week_numbers = list(range(1, 52))
        week = f.selectbox(
            label="Week", options=["This Week", "Next Week"] + week_numbers
        )
        if week == "This Week":
            week = CURRENTWEEKNUMBER
        elif week == "Next Week":
            week = NEXTWEEKNUMBER
        else:
            week = int(week)

    st.title("Player schedule")
    schedule_filters = {}
    if week:
        schedule_filters["week"] = week

    if teams:
        schedule_filters["team"] = teams

    free_agent_filters = {}
    if teams:
        free_agent_filters["team"] = teams

    if free_agent:
        free_agent_filters["player"] = free_agent

    if position:
        free_agent_filters["position"] = position

    if injury:
        free_agent_filters["status"] = injury

    ###
    week_schedule = filter_table(DATASETS.week_vw, schedule_filters)
    week_schedule.reset_index(inplace=True)
    week_schedule = week_schedule.drop(columns=["id", "_ts"])
    free_agents = filter_table(DATASETS.free_agents, free_agent_filters, nr_of_rows)
    free_agents = filter_player_stat_table_colums(free_agents)
    # free_agents = free_agents.set_index("Team")
    # free_agent_schedule = free_agents.join(week_schedule, how="left")
    free_agent_schedule = free_agents.merge(week_schedule, how="left", on="team")
    # free_agent_schedule = format_week_schedule_table(free_agent_schedule)

    st.dataframe(free_agent_schedule, height=400, width=1050)

    # e, f = st.columns(2)
    # e.title("Free Agents")

    # free_agents = filter_table(DATASETS.free_agents, filters, nr_of_rows)
    # free_agents = filter_player_stat_table_colums(free_agents)
    # e.dataframe(free_agents, height=400)

    # f.title("Roster Players")
    # filters = {}
    # if fantasy_roster:
    #     filters["Roster"] = fantasy_roster

    # roster_players = filter_table(DATASETS.roster_players, filters)
    # roster_players = filter_player_stat_table_colums(roster_players)
    # f.dataframe(roster_players, height=400)
