from data.db import DB_URI, DB_PATH
from src.common.utils import fetch_data, filter_df_by_date_range, write_data
import polars as pl
import pandas as pd


def estimate_player_points(
    player_ids: list[int], date: str, days: int, db_uri: str
) -> pl.DataFrame:
    df = fetch_data("SELECT * FROM proj_player_points", db_uri=DB_URI)

    df = df.filter(
        df["player_id"].is_in(player_ids)
        & (df["date"] >= pd.Timestamp(date))
        & (df["date"] <= pd.Timestamp(date) + pd.Timedelta(days=days))
    )

    results = []
    for player_id in player_ids:
        temp_df = df.filter(df["player_id"] == player_id)

        for i in range(1, days + 1):
            filtered_df = filter_df_by_date_range(temp_df, "date", date, i)
            filtered_df = filtered_df.select(
                [
                    "player_id",
                    "name",
                    "avg_points",
                    "projected_avg_points",
                ]
            )
            grouped_df = filtered_df.group_by(["player_id", "name"]).sum()
            grouped_df = grouped_df.with_columns(
                [
                    pl.lit(pd.Timestamp(date)).alias("start_date"),
                    pl.lit(pd.Timestamp(date) + pd.Timedelta(days=i)).alias("end_date"),
                    pl.lit(i).alias("days"),
                ]
            )
            results.append(grouped_df)

    df = pl.concat(results)
    write_data(df=df, table_name="vw_free_agent", db_uri=f"sqlite:///{DB_PATH}")
    return df


if __name__ == "__main__":
    date = "2022-10-18"
    days = 7
    player_ids = [2566769, 3213]
    df = estimate_player_points(player_ids, date, days, db_uri=DB_URI)
    print(df)
