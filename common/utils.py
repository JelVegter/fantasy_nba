from abc import ABC, abstractmethod


class ETL(ABC):
    @abstractmethod
    def fetch_data():
        ...

    @abstractmethod
    def clean_data():
        ...

    @abstractmethod
    def transform_data():
        ...

    @abstractmethod
    def get_data():
        ...
