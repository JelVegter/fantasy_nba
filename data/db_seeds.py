from data.enums import (
    StatTypeEnum,
    StatPeriodEnum,
    StatAggregationTypeEnum,
    TeamEnum,
)
from models.player_stats import (
    StatPeriod,
    StatType,
    StatAggregation,
)
from data.db import Session
from models.team import Team


def clear_tables(session):
    session.query(StatType).delete()
    session.query(StatPeriod).delete()
    session.query(StatAggregation).delete()
    session.query(Team).delete()
    session.commit()


def populate_enum_tables(session):
    for type in StatTypeEnum:
        session.add(StatType(name=type.name))
    for period in StatPeriodEnum:
        session.add(StatPeriod(name=period.name))
    for agg in StatAggregationTypeEnum:
        session.add(StatAggregation(name=agg.name))
    for team in TeamEnum:
        session.add(Team(abbrev=team.name, name=team.value))
    session.commit()


if __name__ == "__main__":
    with Session() as session:
        try:
            clear_tables(session)
        finally:
            populate_enum_tables(session)
