from src.espn.league import league
from data.db import Session
from models.player import Player
from sqlalchemy import func, insert
from src.espn.league import YEAR

FREE_AGENT = "Free Agent"


def insert_players(session, all_players: list[Player]):
    current_time = func.now()
    for fantasy_roster_name, players in all_players.items():
        for player in players:

            if player.injuryStatus == []:
                player.injuryStatus = None
            stmt = (
                insert(Player)
                .prefix_with("OR IGNORE")
                .values(
                    player_id=player.playerId,
                    name=player.name,
                    fantasy_roster_name=fantasy_roster_name,
                    is_free_agent=1 if fantasy_roster_name == FREE_AGENT else 0,
                    team_abbrev=player.proTeam,
                    position=player.position,
                    injury_status=player.injuryStatus,
                    injured=player.injured,
                    lineup_slot=player.lineupSlot,
                    total_points=player.total_points,
                    avg_points=player.avg_points,
                    avg_last_7=player.stats[f"{YEAR}_last_7"]["applied_avg"],
                    avg_last_15=player.stats[f"{YEAR}_last_15"]["applied_avg"],
                    avg_last_30=player.stats[f"{YEAR}_last_30"]["applied_avg"],
                    projected_total_points=player.projected_total_points,
                    projected_avg_points=player.projected_avg_points,
                    created_at=current_time,
                    modified_at=current_time,
                )
            )
            session.execute(stmt)


if __name__ == "__main__":
    all_players = {FREE_AGENT: league.free_agents(size=200)}
    for roster in league.teams:
        all_players[roster.team_name] = list(roster.roster)

    with Session() as session:
        try:
            insert_players(session, all_players)
            session.commit()
        except Exception as e:
            print(f"Error occurred: {e}")
            session.rollback()
            raise e
