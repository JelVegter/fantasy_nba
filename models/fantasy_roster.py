from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from models.base import Base


class FantasyRoster(Base):
    __tablename__ = "fantasy_roster"

    id = Column(Integer, primary_key=True)
    abbrev = Column(String, nullable=True)
    name = Column(String, nullable=True)
    division_id = Column(String, nullable=True)
    division_name = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    standing = Column(Integer, nullable=True)
    final_standing = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    players = relationship("Player", back_populates="roster")
    # league = relationship("FantasyRoster", back_populates="league")s
