from sqlalchemy import (
    Column,
    UniqueConstraint,
    Integer,
    ForeignKey,
    Float,
    Enum as SQLAEnum,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship
from models.base import Base
from data.enums import StatPeriodEnum, StatTypeEnum, StatAggregationTypeEnum


class StatPeriod(Base):
    __tablename__ = "stat_period"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(SQLAEnum(StatPeriodEnum), nullable=False)


class StatType(Base):
    __tablename__ = "stat_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(SQLAEnum(StatTypeEnum), nullable=False)


class StatAggregation(Base):
    __tablename__ = "stat_aggregation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(SQLAEnum(StatAggregationTypeEnum), nullable=False)


class PlayerStats(Base):
    __tablename__ = "player_stats"

    def __init__(self, *args, **kwargs):
        super(PlayerStats, self).__init__(*args, **kwargs)
        self.is_free_agent = 1 if kwargs.get("roster_id") == -1 else 0

    id = Column(Integer, primary_key=True, autoincrement=True)

    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    roster_id = Column(Integer, ForeignKey("fantasy_roster.id"), nullable=False)
    stat_period_id = Column(Integer, ForeignKey("stat_period.id"), nullable=False)
    stat_aggregation_id = Column(
        Integer, ForeignKey("stat_aggregation.id"), nullable=False
    )
    is_free_agent = Column(Integer, default=0)
    applied_value = Column(Float)
    for stat, _ in StatTypeEnum.__members__.items():
        locals()[stat.lower()] = Column(Float, nullable=True)

    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # player = relationship("Player")
    # team = relationship("Team")
    # roster = relationship("FantasyRoster")
    # period = relationship("StatPeriod")
    # aggregation = relationship("StatAggregation")

    # __table_args__ = (
    #     UniqueConstraint(
    #         "player_id",
    #         "team_id",
    #         "roster_id",
    #         "stat_period_id",
    #         "stat_aggregation_id",
    #         "is_free_agent",
    #         "applied_value",
    #         # *[stat for stat in StatTypeEnum.__members__.keys()],
    #         name="_unique_row_constraint",
    #     ),
    # )
