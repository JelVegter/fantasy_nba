from data.db import DB_PATH, DB_URI
from src.common.utils import fetch_data, write_data


def main():
    player_df = fetch_data(query="SELECT * FROM player", db_uri=DB_URI)
    schedule_df = fetch_data(query="SELECT * FROM schedule", db_uri=DB_URI)
    merged_df = player_df.join(schedule_df, on="team_abbrev")
    final_df = merged_df.select(
        [
            "player_id",
            "name",
            "date",
            "time",
            "week",
            "day_of_year",
            "day_of_week",
            "total_points",
            "avg_points",
            "projected_total_points",
            "projected_avg_points",
            "injury_status",
            "injured",
            "team_abbrev",
            "fantasy_roster_name",
            "position",
            "opponent_abbrev",
            "is_visitor",
            "is_free_agent",
        ]
    )
    write_data(
        df=final_df, table_name="proj_player_points", db_uri=f"sqlite:///{DB_PATH}"
    )


if __name__ == "__main__":
    main()
