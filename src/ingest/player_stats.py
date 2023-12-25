# from data.db import Session
# from src.espn.league import league
# from data.enums import StatTypeEnum, StatPeriodEnum
# from models.team import Team
# from models.player_stats import StatPeriod, StatAggregation, PlayerStats
# from sqlalchemy import insert


# def get_enum_mapping(enum_class):
#     return {e.value: e.name for e in enum_class}


# def get_team_id(session, abbrev):
#     return session.query(Team.id).filter(Team.abbrev == abbrev).one()[0]


# def get_stat_id(session, enum_mapping, period):
#     try:
#         return (
#             session.query(StatPeriod.id)
#             .filter(StatPeriod.name == enum_mapping[period])
#             .one()[0]
#         )
#     except Exception as e:
#         print(f"Error fetching stat ID for period {period}: {str(e)}")
#         return None


# def get_aggregation_id(session, stat_type):
#     try:
#         return (
#             session.query(StatAggregation.id)
#             .filter(StatAggregation.name == stat_type.upper())
#             .one()[0]
#         )
#     except Exception as e:
#         print(f"Error fetching aggregation ID for stat type {stat_type}: {str(e)}")
#         return None


# def process_player_stats(session, player, roster_id, period, stat_type, enum_mapping):
#     applied_value_key = f"applied_{stat_type}"
#     applied_value = player.stats[period][applied_value_key]

#     if stats := player.stats[period].get(stat_type, {}):
#         stats = {
#             enum_mapping[key].lower(): value
#             for key, value in stats.items()
#             if key in enum_mapping
#         }

#         if aggregation_id := get_aggregation_id(session, stat_type):
#             # Creating an instance without adding it to the session
#             # player_stat_instance = PlayerStats(
#             #     player_id=player.playerId,
#             #     team_id=get_team_id(session, player.proTeam),
#             #     roster_id=roster_id,
#             #     stat_period_id=get_stat_id(session, stat_period_enum_mapping, period),
#             #     stat_aggregation_id=aggregation_id,
#             #     applied_value=applied_value,
#             #     **stats,
#             # )
#             stmt = (
#                 insert(PlayerStats)
#                 .prefix_with("OR IGNORE")
#                 .values(
#                     player_id=player.playerId,
#                     team_id=get_team_id(session, player.proTeam),
#                     roster_id=roster_id,
#                     stat_period_id=get_stat_id(
#                         session, stat_period_enum_mapping, period
#                     ),
#                     stat_aggregation_id=aggregation_id,
#                     applied_value=applied_value,
#                     **stats,
#                 )
#             )
#             session.execute(stmt)

#             # # Check if content_uuid already exists
#             # if not does_content_uuid_exist(
#             #     session, PlayerStats, player_stat_instance.content_uuid
#             # ):
#             #     session.merge(player_stat_instance)


# if __name__ == "__main__":
#     session = Session()
#     failed_periods = []

#     stat_type_enum_mapping = get_enum_mapping(StatTypeEnum)
#     stat_period_enum_mapping = get_enum_mapping(StatPeriodEnum)

#     all_players = {"free_agent": league.free_agents(size=200)}
#     for roster in league.teams:
#         all_players[roster.team_id] = list(roster.roster)

#     for _roster_id, players in all_players.items():
#         roster_id = -1 if _roster_id == "free_agent" else _roster_id
#         for player in players:
#             for period, _ in player.stats.items():
#                 if period not in stat_period_enum_mapping:
#                     failed_periods.append(period)
#                     continue
#                 for stat_type in ["avg", "total"]:
#                     process_player_stats(
#                         session,
#                         player,
#                         roster_id,
#                         period,
#                         stat_type,
#                         stat_type_enum_mapping,
#                     )

#     session.commit()
#     session.close()
#     print(set(failed_periods))
