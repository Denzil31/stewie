from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DatabaseConfigInterface:
    pass


class DatabaseInterface(ABC):
    @abstractmethod
    def add_url_mapping(self, short_code, long_url, expires_at):
        pass

    @abstractmethod
    def get_url_mapping(self, short_code):
        pass
