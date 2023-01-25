import sqlite3
from common.db import DBConnection
from common.dt import format_datetime
from pandas import DataFrame, read_sql, read_sql_query
from typing import Optional
from datetime import datetime
import hashlib


def get_hashed_id(*values) -> str:
    _str = ""
    for value in values:
        if not isinstance(value, str):
            value = str(value)
        _str = "".join([_str, value])
    _bytes = _str.encode("utf-8")
    return hashlib.md5(_bytes).hexdigest()


class SQLDBConnection(DBConnection):
    def __init__(self, db_file: str):
        self.db_file = db_file

    def _fetch_cursor(self):
        with sqlite3.connect(self.db_file) as db_conn:
            return db_conn.cursor()

    def execute_query(self, query):
        cursor = self._fetch_cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def fetch_tables_in_db(self) -> list[str]:
        query = """ SELECT name
                    FROM sqlite_schema
                    WHERE type ='table'
                    AND name NOT LIKE 'sqlite_%';
                    """
        return self.execute_query(query)

    def df_to_sql_table(
        self,
        df: DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        auto_id_cols: Optional[list[str]] = None,
    ):
        df["_ts"] = format_datetime(datetime.now())
        if auto_id_cols:
            df["id"] = df.apply(lambda x: get_hashed_id(x[auto_id_cols]), axis=1)
            df = df.set_index("id")

        df.columns = df.columns.str.lower()
        index = True if auto_id_cols else False
        with sqlite3.connect(self.db_file) as db_conn:
            df.to_sql(
                name=table, schema=schema, con=db_conn, if_exists=if_exists, index=index
            )

    def sql_query_to_df(self, query: str) -> DataFrame:
        with sqlite3.connect(self.db_file) as db_conn:
            return read_sql_query(sql=query, con=db_conn)

    def sql_table_to_df(
        self,
        table: str,
        schema: Optional[str] = None,
        limit: Optional[int] = None,
        date_cols: Optional[list[str]] = None,
    ) -> DataFrame:
        table = ".".join([schema, table]) if schema else table
        limit = f"LIMIT {limit}" if limit else ""
        query = f"SELECT * FROM {table} {limit}"
        with sqlite3.connect(self.db_file) as db_conn:
            return read_sql(sql=query, con=db_conn, parse_dates=date_cols)

    def deduplicate_table(self, table: str, column: str = "id") -> None:
        query = f"""DELETE FROM {table}
                    WHERE rowid NOT IN (
                        SELECT MIN(rowid)
                        FROM {table}
                        GROUP BY {column}
                        HAVING COUNT(*) > 1)
                    """
        self.execute_query(query)


sqlite3_conn = SQLDBConnection("db/sqlite_fantasynba")
