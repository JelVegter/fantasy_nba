import logging
from pandas import DataFrame


def hover(hover_color="#013220"):
    return dict(selector="tr:hover", props=[("background-color", "%s" % hover_color)])


styles = [
    hover(),
    dict(selector="th", props=[("font-size", "150%"), ("text-align", "center")]),
    dict(selector="caption", props=[("caption-side", "bottom")]),
]


def highlight_teams_playing(value: str) -> str:
    color = "Black"
    if isinstance(value, str):
        if len(value) > 2:
            color = "#013220"
    return "background-color: %s" % color


def format_week_schedule_table(df: DataFrame) -> DataFrame:
    df = (
        df.set_index("team")
        .style.set_table_styles(styles)
        .set_caption("Hover to highlight.")
        .applymap(highlight_teams_playing)
    )
    return df


def filter_player_stat_table_colums(df: DataFrame) -> DataFrame:
    df = df.rename(columns={"projected_fantasy_points": "points"})
    cols = [
        "player",
        "team",
        "position",
        "status",
        "points",
        "today",
        "nexttwodays",
        "thisweek",
        "nextweek",
    ]
    return df[cols]


def filter_table(
    df: DataFrame,
    filters: dict = None,
    nr_of_rows: int = None,
) -> DataFrame:

    if not isinstance(df, DataFrame):
        message = f"Data passed through is not a dataframe but of type: {type(df)}"
        logging.critical(message)
        raise Exception(message)

    if filters:
        for filter, value in filters.items():
            try:
                if isinstance(value, (str, int)):
                    df = df.loc[df[filter] == filters[filter]]

                elif isinstance(filters[filter], list):
                    df["team"] = df["team"].astype(str)
                    df = df.loc[df[filter].isin(filters[filter])]
                else:
                    raise ValueError("Filter type not accepted")

            except ValueError as e:
                logging.critical(f"Columns to filter on: {filter}")
                logging.critical(f"Column value example: {df[filter].iloc[0]}")
                logging.critical(f"Column value type: {df[filter].dtype}")
                logging.critical(f"Filter type: {type(filters[filter])}")
                logging.critical(f"Filter value: {filters[filter]}")
                raise e
    if nr_of_rows:
        df = df.head(nr_of_rows)

    return df
