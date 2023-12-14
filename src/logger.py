import enum
import logging
import sys


class LogLevelColors(enum.StrEnum):
    DEBUG = '\033[97m'
    INFO = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m' 
    CRITICAL = '\033[31m'
    RESET = '\033[0m'


class Formatter(logging.Formatter):

    def __init__(self) -> None:
        super().__init__("[%(asctime)s] -- %(pathname)s:%(lineno)d -- %(levelname)s -- %(message)s")


    def format(self, record: logging.LogRecord):
        color, end = LogLevelColors.RESET, LogLevelColors.RESET
        return f"{color}{super().format(record)}{end}"

class Logger(logging.Logger):

    def __init__(self, *, name: str, level: int = logging.INFO) -> None:
        super().__init__(name, level)
        self._handler = logging.StreamHandler(stream=sys.stdout)
        self.__setup()

    def __setup(self) -> None:
        self._handler.setFormatter(Formatter())
        self.addHandler(self._handler)


