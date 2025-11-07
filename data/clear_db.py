from models.base import Base
from data.db import DB_ENGINE, Session
from sqlalchemy import text


def clear_db() -> None:
    session = Session()
    with DB_ENGINE.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = OFF"))
        Base.metadata.drop_all(DB_ENGINE)
        connection.execute(text("PRAGMA foreign_keys = ON"))
    session.commit()
    session.close()


if __name__ == "__main__":
    clear_db()
