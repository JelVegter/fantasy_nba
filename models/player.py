from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from models.base import Base


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    team_abbrev = Column(String, ForeignKey("team.abbrev"))
    fantasy_roster_name = Column(String, ForeignKey("fantasy_roster.name"))
    is_free_agent = Column(Integer, nullable=False)
    position = Column(String, nullable=True)
    injury_status = Column(String, nullable=True)
    injured = Column(Integer, nullable=True)
    lineup_slot = Column(String, nullable=True)
    total_points = Column(Float, nullable=True)
    avg_points = Column(Float, nullable=True)
    projected_total_points = Column(Float, nullable=True)
    projected_avg_points = Column(Float, nullable=True)

    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    roster = relationship("FantasyRoster", back_populates="players")
    team = relationship("Team", back_populates="players")

    __table_args__ = (
        UniqueConstraint(
            "name",
            "team_abbrev",
            "fantasy_roster_name",
            "total_points",
            "avg_points",
            "projected_total_points",
            "projected_avg_points",
            name="unique_player",
        ),
    )
