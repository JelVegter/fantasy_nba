import logging
from logging.config import fileConfig
import streamlit as st
from render.multipage import MultiPage
from render import free_agent
from render import team_schedule
from render import game_gap
from render import matchup


def main():
    st.set_page_config(  # Alternate names: setup_page, page, layout
        layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
        initial_sidebar_state="expanded",  # Can be "auto", "expanded", "collapsed"
        page_title=None,  # String or None. Strings get appended with "• Streamlit".
        page_icon=None,  # String, anything supported by st.image, or None.
    )

    # ---------------------------------------------#
    # ---------------  DEFINE PAGES ---------------#
    # ---------------------------------------------#
    app = MultiPage()
    app.add_page("Free Agents", free_agent.app)
    app.add_page("Team Schedule", team_schedule.app)
    app.add_page("Game Gap", game_gap.app)
    app.add_page("Matchup", matchup.app)
    app.run()


if __name__ == "__main__":
    DEBUG_MODE = True
    main()
