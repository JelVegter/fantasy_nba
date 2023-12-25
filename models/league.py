from sqlalchemy import Column, Integer, DateTime, func

# from sqlalchemy.orm import relationship
from models.base import Base


class League(Base):
    __tablename__ = "fantasy_nba_league"

    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # fantasy_roter = relationship("FantasyRoster", back_populates="league")
