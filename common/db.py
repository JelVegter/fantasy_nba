from pandas import DataFrame
from abc import ABC, abstractmethod


class DBConnection(ABC):
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def _fetch_cursor(self):
        ...

    @abstractmethod
    def execute_query(self):
        ...

    @abstractmethod
    def fetch_tables_in_db(self):
        ...

    @abstractmethod
    def df_to_sql_table(self):
        ...

    @abstractmethod
    def sql_table_to_df(self) -> DataFrame:
        ...

    @abstractmethod
    def sql_query_to_df(self) -> DataFrame:
        ...

    @abstractmethod
    def deduplicate_table(self):
        ...
