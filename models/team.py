from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SQLAEnum,
    DateTime,
    func,
)
from models.base import Base
from data.enums import TeamEnum
from sqlalchemy.orm import relationship


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    abbrev = Column(SQLAEnum(TeamEnum), nullable=True)
    name = Column(String)

    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    players = relationship("Player", back_populates="team")
