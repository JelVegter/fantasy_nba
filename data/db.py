from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DB_PATH = "data/fantasy_nba.db"
DB_URI = f"sqlite://{DB_PATH}"
DB_ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=True)
Session = sessionmaker(bind=DB_ENGINE)
