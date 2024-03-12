from data.db import Session
from src.espn.league import league
from models.fantasy_roster import FantasyRoster
from sqlalchemy import func, insert

if __name__ == "__main__":
    session = Session()

    # Insert or update Free Agent Roster
    current_time = func.now()
    stmt = (
        insert(FantasyRoster)
        .prefix_with("OR REPLACE")
        .values(
            id=-1, name="Free Agent", created_at=current_time, modified_at=current_time
        )
    )
    session.execute(stmt)
    for roster in league.teams:
        stmt = (
            insert(FantasyRoster)
            .prefix_with("OR REPLACE")
            .values(
                id=roster.team_id,
                abbrev=roster.team_abbrev,
                name=roster.team_name,
                division_id=roster.division_id,
                division_name=roster.division_name,
                # owner=roster.owner,
                standing=roster.standing,
                final_standing=roster.final_standing,
                created_at=current_time,
                modified_at=current_time,
            )
        )
        session.execute(stmt)
    session.commit()
    session.close()
