from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(timezone=True), nullable=False)
    day_of_year = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    time = Column(String(5), nullable=False)
    opponent_abbrev = Column(String(3), nullable=False)
    team_abbrev = Column(String(3), nullable=False)
    matchup = Column(String(7), nullable=False)
    is_visitor = Column(Integer, nullable=False)
