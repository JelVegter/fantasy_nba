import logging
from logging.config import fileConfig
import streamlit as st

from multipage import MultiPage
import schedule


def main(debug: bool = False):
    if debug:
        fileConfig("logging.ini")
        logging.getLogger("dev")

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
    app.add_page("Schedule", schedule.app)
    # app.add_page("Free Players", page_free_agents.app)
    # app.add_page("Player Streaming", page_streaming.app)
    # app.add_page("Matchup Comparison", page_matchup_comparison.app)
    # app.add_page("Y-Parameter Optimization",redundant.app)
    app.run()


if __name__ == "__main__":
    main()
