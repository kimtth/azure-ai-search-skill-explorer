from abc import ABC


class BaseParser(ABC):
    def parse_by_filepath(self, file_path: str) -> dict:
        pass
