from abc import ABC, abstractmethod


class DataGetter(ABC):
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
    def export_data():
        ...

    @abstractmethod
    def read_data():
        ...

    @abstractmethod
    def get_data():
        ...
