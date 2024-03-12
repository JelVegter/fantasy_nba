import streamlit as st
from src.common.constants import DATETIME_PRETTY, CURRENTWEEKNUMBER


class MultiPage:
    """Framework for combining multiple streamlit applications."""

    def __init__(self) -> None:
        """Constructor to generate a list which will store all our applications as an instance variable."""
        self.pages = []

    def add_page(self, title, func) -> None:
        """Method to add pages to the project.

        Args:
            title (str): The title of the page which we are adding to the list of apps.
            func: Python function to render this page in Streamlit.
        """
        self.pages.append({"title": title, "function": func})

    def run(self):
        # Sidebar with Time, Week and App Navigation
        st.sidebar.markdown(f"**Time (ET):** {DATETIME_PRETTY}")
        st.sidebar.markdown(f"**Week:** {CURRENTWEEKNUMBER}")
        page = st.sidebar.selectbox(
            "Select a Page:", self.pages, format_func=lambda page: page["title"]
        )
        st.sidebar.markdown("---")

        # Horizontal line

        # Run the app function
        page["function"]()
